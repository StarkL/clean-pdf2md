"""CleanPDF2MD: Lightweight, Zero-GPU PDF-to-Markdown Converter with Smart Noise Removal and Image Anchoring."""

__version__ = "0.1.0"
__author__ = "CleanPDF2MD Contributors"
__license__ = "MIT"

from .converter import CleanPDFConverter
from .presets import get_preset, BasePreset, WeChatPreset, ZhihuPreset, GenericPreset

__all__ = [
    "CleanPDFConverter",
    "get_preset",
    "BasePreset",
    "WeChatPreset",
    "ZhihuPreset",
    "GenericPreset",
    "__version__",
]
