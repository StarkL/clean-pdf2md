import os
import re
import fitz
from typing import Optional, List, Tuple, Callable
from rapidocr_onnxruntime import RapidOCR
from .presets import get_preset, BasePreset

class CleanPDFConverter:
    """Core converter from rasterized / print-to-PDF to structured Markdown with images."""

    def __init__(
        self,
        preset: str = "wechat",
        min_width: int = 250,
        min_height: int = 150,
        min_size: int = 12000,
        dpi: int = 150,
        custom_preset: Optional[BasePreset] = None
    ):
        self.preset: BasePreset = custom_preset or get_preset(preset)
        self.min_width = min_width
        self.min_height = min_height
        self.min_size = min_size
        self.dpi = dpi
        self._ocr = None

    @property
    def ocr(self) -> RapidOCR:
        """Lazy load OCR engine to avoid overhead in sub-processes or lightweight calls."""
        if self._ocr is None:
            self._ocr = RapidOCR()
        return self._ocr

    def extract_images(self, doc: fitz.Document, page_num: int, target_dir: str, rel_prefix: str) -> List[Tuple[str, int, int]]:
        """Extract high-resolution content images from page XRef stream."""
        page = doc[page_num]
        img_list = page.get_images()
        extracted = []
        seen_xrefs = set()

        for img_info in img_list:
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                base_img = doc.extract_image(xref)
                w, h = base_img["width"], base_img["height"]
                raw_bytes = base_img["image"]

                if w >= self.min_width and h >= self.min_height and len(raw_bytes) >= self.min_size:
                    ext = base_img["ext"]
                    filename = f"p{page_num + 1}_{xref}.{ext}"
                    filepath = os.path.join(target_dir, filename)

                    with open(filepath, "wb") as f:
                        f.write(raw_bytes)

                    rel_path = f"{rel_prefix}/{filename}".replace("\\", "/")
                    extracted.append((rel_path, w, h))
            except Exception:
                pass

        return extracted

    def convert(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        overwrite: bool = False,
        progress_cb: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[bool, str, str]:
        """Convert a single PDF file into structured Markdown with extracted images.
        
        Returns:
            (success: bool, output_md_path: str, message: str)
        """
        if not os.path.exists(pdf_path):
            return False, "", f"File not found: {pdf_path}"

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(pdf_path))

        out_md_path = os.path.join(output_dir, f"{base_name}.md")

        if not overwrite and os.path.exists(out_md_path) and os.path.getsize(out_md_path) > 1000:
            return True, out_md_path, f"Skipped (already converted): {base_name}.md"

        # Safe directory identifier
        m = re.match(r'^(\d+)', base_name)
        art_idx = m.group(1) if m else re.sub(r'[\W_]+', '_', base_name)[:20]

        img_output_dir = os.path.join(output_dir, "images", art_idx)
        os.makedirs(img_output_dir, exist_ok=True)
        rel_img_prefix = f"images/{art_idx}"

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            return False, "", f"Error reading PDF {base_name}: {e}"

        total_pages = len(doc)
        page_texts = []
        is_after_content = False

        for pno in range(total_pages):
            if is_after_content:
                break

            if progress_cb:
                progress_cb(pno + 1, total_pages, f"Processing page {pno + 1}/{total_pages}")

            # 1. Extract genuine images from this page
            page_imgs = self.extract_images(doc, pno, img_output_dir, rel_img_prefix)

            # 2. Render page to image at specified DPI for OCR
            page = doc[pno]
            pix = page.get_pixmap(dpi=self.dpi)
            img_bytes = pix.tobytes("png")

            res, _ = self.ocr(img_bytes)
            if not res:
                if page_imgs and not is_after_content:
                    imgs_md = "\n\n".join([f"![插图]({rpath})" for rpath, _, _ in page_imgs])
                    page_texts.append(imgs_md)
                continue

            # Sort detected boxes top-to-bottom
            res.sort(key=lambda x: x[0][0][1])

            cleaned_lines = []
            for item in res:
                text = item[1].strip()
                if not text:
                    continue

                # Check for content cutoff (e.g. comments/footer)
                if self.preset.is_content_cutoff(text, pno):
                    is_after_content = True
                    break

                # Filter header noise
                if self.preset.should_filter_header(text, pno):
                    continue

                # Format heading
                heading = self.preset.format_heading(text)
                if heading:
                    cleaned_lines.append(heading)
                else:
                    cleaned_lines.append(text)

            # Stitch Chinese paragraphs
            merged_lines = []
            buf = ""
            for line in cleaned_lines:
                if line.startswith("#") or line.startswith("- ") or line.startswith("* ") or re.match(r'^\d+\.', line):
                    if buf:
                        merged_lines.append(buf)
                        buf = ""
                    merged_lines.append(line)
                else:
                    if buf:
                        if buf[-1] in "。！？；":
                            merged_lines.append(buf)
                            buf = line
                        else:
                            buf += line
                    else:
                        buf = line
            if buf:
                merged_lines.append(buf)

            page_content = "\n\n".join(merged_lines)

            # Append page images
            if page_imgs and not is_after_content:
                imgs_md = "\n\n".join([f"![插图]({rpath})" for rpath, _, _ in page_imgs])
                if page_content:
                    page_content += "\n\n" + imgs_md
                else:
                    page_content = imgs_md

            if page_content.strip():
                page_texts.append(page_content)

        # Assemble full document
        full_md = f"# {base_name}\n\n" + "\n\n---\n\n".join(page_texts) + "\n"

        with open(out_md_path, "w", encoding="utf-8") as f:
            f.write(full_md)

        return True, out_md_path, f"Done ({len(page_texts)} pages processed)"

    def convert_batch(
        self,
        input_dir: str,
        output_dir: str,
        overwrite: bool = False
    ) -> List[Tuple[str, bool, str]]:
        """Batch convert all PDF files in input_dir."""
        os.makedirs(output_dir, exist_ok=True)
        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
        pdf_files.sort()

        results = []
        total = len(pdf_files)
        print(f"Found {total} PDF files to convert in {input_dir}.")

        for i, fn in enumerate(pdf_files, 1):
            pdf_path = os.path.join(input_dir, fn)
            print(f"[{i:02d}/{total}] Converting: {fn} ...", flush=True)
            ok, out_path, msg = self.convert(pdf_path, output_dir=output_dir, overwrite=overwrite)
            print(f"       -> {msg}", flush=True)
            results.append((fn, ok, msg))

        return results
