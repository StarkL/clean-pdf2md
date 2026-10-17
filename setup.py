from setuptools import setup, find_packages

setup(
    name="clean-pdf2md",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pymupdf>=1.24.0",
        "rapidocr-onnxruntime>=1.3.0",
        "pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "clean-pdf2md=clean_pdf2md.cli:main",
        ],
    },
)
