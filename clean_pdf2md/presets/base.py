from abc import ABC, abstractmethod
import re
from typing import List, Optional

class BasePreset(ABC):
    """Base class for document cleaning presets."""
    name: str = "base"
    description: str = "Base Preset"

    @abstractmethod
    def should_filter_header(self, text: str, page_num: int) -> bool:
        """Return True if this line should be discarded as header noise."""
        pass

    @abstractmethod
    def is_content_cutoff(self, text: str, page_num: int) -> bool:
        """Return True if this line triggers the end of meaningful article content (e.g. comments/footer)."""
        pass

    def format_heading(self, text: str) -> Optional[str]:
        """Optionally rewrite text into a Markdown heading (# / ## / ###) if it matches pattern."""
        # Generic Chinese numbering (e.g., 一、 二、)
        if re.match(r'^[一二三四五六七八九十]+[、.]', text):
            return f"## {text}"
        # Numeric indexing (e.g., 1. 2. 1.1)
        if re.match(r'^\d+[、.][\u4e00-\u9fa5a-zA-Z]', text) and len(text) < 35:
            return f"### {text}"
        # Common structural keywords
        if text.startswith("总结") or text.startswith("前言") or text.startswith("背景") or text.startswith("小结"):
            return f"## {text}"
        return None
