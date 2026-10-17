import argparse
import os
import sys
from clean_pdf2md.converter import CleanPDFConverter
from clean_pdf2md.presets import PRESETS
from clean_pdf2md import __version__

def main():
    parser = argparse.ArgumentParser(
        prog="clean-pdf2md",
        description="CleanPDF2MD: Lightweight, Zero-GPU PDF-to-Markdown Converter with Smart Noise Removal and Image Anchoring."
    )
    parser.add_argument(
        "input",
        help="Path to a PDF file or a directory containing PDF files."
    )
    parser.add_argument(
        "-o", "--output",
        default="./output_markdown",
        help="Output directory for generated Markdown files and extracted images (default: ./output_markdown)."
    )
    parser.add_argument(
        "-p", "--preset",
        default="wechat",
        choices=list(PRESETS.keys()),
        help=f"Cleaning preset to apply: {', '.join(PRESETS.keys())} (default: wechat)."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing Markdown files instead of skipping."
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Rendering DPI for OCR detection (default: 150)."
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=250,
        help="Minimum width in pixels for extracted content images (default: 250)."
    )
    parser.add_argument(
        "--min-height",
        type=int,
        default=150,
        help="Minimum height in pixels for extracted content images (default: 150)."
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=12000,
        help="Minimum file size in bytes for extracted content images (default: 12000)."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    converter = CleanPDFConverter(
        preset=args.preset,
        min_width=args.min_width,
        min_height=args.min_height,
        min_size=args.min_size,
        dpi=args.dpi
    )

    print("=" * 60)
    print(f" CleanPDF2MD v{__version__} - Lightweight PDF to Markdown")
    print(f" Preset: {args.preset.upper()}")
    print(f" Input:  {input_path}")
    print(f" Output: {output_dir}")
    print("=" * 60)

    if os.path.isfile(input_path):
        print(f"Converting single file: {os.path.basename(input_path)} ...")
        ok, out_path, msg = converter.convert(input_path, output_dir=output_dir, overwrite=args.overwrite)
        print(f"Result: {msg}")
        if ok:
            print(f"Markdown saved to: {out_path}")
            sys.exit(0)
        else:
            sys.exit(1)
    elif os.path.isdir(input_path):
        results = converter.convert_batch(input_path, output_dir=output_dir, overwrite=args.overwrite)
        success_count = sum(1 for _, ok, _ in results if ok)
        print("=" * 60)
        print(f"Batch conversion completed! {success_count}/{len(results)} files converted successfully.")
        print(f"Output files located at: {output_dir}")
        print("=" * 60)
    else:
        print(f"Error: Target path does not exist: {input_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
