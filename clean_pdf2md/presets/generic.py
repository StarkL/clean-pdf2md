from .base import BasePreset

class GenericPreset(BasePreset):
    """Generic preset for standard documents without aggressive platform cutoffs."""
    name: str = "generic"
    description: str = "Generic Preset (standard text extraction and heading formatting)"

    def should_filter_header(self, text: str, page_num: int) -> bool:
        return False

    def is_content_cutoff(self, text: str, page_num: int) -> bool:
        return False
