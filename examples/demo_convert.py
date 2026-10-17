"""Example showing Python API usage of CleanPDF2MD."""

import os
from clean_pdf2md import CleanPDFConverter

def run_demo():
    # 1. Initialize converter with WeChat preset
    converter = CleanPDFConverter(preset="wechat", dpi=150)

    # 2. Convert single PDF
    sample_pdf = os.path.abspath(r"../ai-agent-course-code/docs/03. 前言：Agent 课程脉络梳理，有方向感的学.pdf")
    output_dir = os.path.abspath("./demo_output")

    if os.path.exists(sample_pdf):
        print(f"Converting demo PDF: {sample_pdf}")
        success, out_path, msg = converter.convert(sample_pdf, output_dir=output_dir, overwrite=True)
        print(f"Status: {msg}")
        print(f"Generated Markdown: {out_path}")
    else:
        print(f"Sample PDF not found at {sample_pdf}, please specify a valid PDF path.")

if __name__ == "__main__":
    run_demo()
