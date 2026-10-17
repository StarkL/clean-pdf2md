import re
from .base import BasePreset

class ZhihuPreset(BasePreset):
    """Preset optimized for Zhihu columns, answers, and Yanxuan stories."""
    name: str = "zhihu"
    description: str = "Zhihu Preset (cleans upvote banners, badges, and comment sections)"

    HEADER_KEYWORDS = [
        "知乎", "知乎专栏", "盐选专栏", "盐选推荐", "开通盐选", "会员专享"
    ]

    CUTOFF_TRIGGERS = [
        "添加评论", "条评论", "赞同", "反对", "喜欢", "收藏", "分享到微信",
        "收起", "相关推荐", "查看更多评论"
    ]

    def should_filter_header(self, text: str, page_num: int) -> bool:
        if page_num == 0:
            if any(k in text for k in self.HEADER_KEYWORDS):
                return True
            if "编辑于" in text or "发布于" in text:
                return True
        return False

    def is_content_cutoff(self, text: str, page_num: int) -> bool:
        if len(text) > 18:
            return False
        return any(trigger in text for trigger in self.CUTOFF_TRIGGERS)
