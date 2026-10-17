from typing import Dict, Type
from .base import BasePreset
from .wechat import WeChatPreset
from .zhihu import ZhihuPreset
from .generic import GenericPreset

PRESETS: Dict[str, Type[BasePreset]] = {
    "wechat": WeChatPreset,
    "zhihu": ZhihuPreset,
    "generic": GenericPreset,
}

def get_preset(name: str = "wechat") -> BasePreset:
    """Factory to instantiate preset by name."""
    cls = PRESETS.get(name.lower(), GenericPreset)
    return cls()

__all__ = ["BasePreset", "WeChatPreset", "ZhihuPreset", "GenericPreset", "get_preset", "PRESETS"]
