import re
from .base import BasePreset

class WeChatPreset(BasePreset):
    """Preset optimized for WeChat Official Account articles printed to PDF."""
    name: str = "wechat"
    description: str = "WeChat Official Account Preset (cleans headers, dates, and comment sections)"

    HEADER_KEYWORDS = [
        "已付费", "人付费", "原创", "神光的幸福生活", "微信公众号", "阅读原文",
        "神说要有光"
    ]

    # Broad triggers: if line contains these and is relatively short, it's a cutoff
    COMMENT_SECTION_TRIGGERS = [
        "写留言", "精选留言", "全部留言", "首评",
        "作者回复", "条回复", "微信扫一扫", "关注该公众号"
    ]

    # Exact or short button triggers (e.g., "在看", "点赞", "赞赏")
    INTERACTION_BUTTONS = [
        "在看", "点赞", "赞赏", "分享", "收藏"
    ]

    PROVINCES = [
        "山东", "北京", "上海", "广东", "浙江", "江苏", "杭州", "深圳", "四川",
        "湖北", "湖南", "河南", "河北", "陕西", "安徽", "福建", "重庆", "天津",
        "辽宁", "吉林", "黑龙江", "江西", "贵州", "云南", "山西", "内蒙古", "广西"
    ]

    def should_filter_header(self, text: str, page_num: int) -> bool:
        if page_num == 0:
            if any(k in text for k in self.HEADER_KEYWORDS):
                return True
            if re.match(r'^\d{4}年\d{1,2}月\d{1,2}日', text):
                return True
            if text in self.PROVINCES:
                return True
            # Match date like "2026-07-19"
            if re.match(r'^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}', text):
                return True
        return False

    def is_content_cutoff(self, text: str, page_num: int) -> bool:
        trimmed = text.strip()
        # 1. Broad comment headers (e.g. "留言 25", "写留言")
        if len(trimmed) < 18:
            if any(trigger in trimmed for trigger in self.COMMENT_SECTION_TRIGGERS):
                return True
            if re.match(r'^留言\s*\d*', trimmed):
                return True

        # 2. Standalone interaction buttons (e.g. "在看 12", "点赞", "赞赏")
        if len(trimmed) <= 8:
            for btn in self.INTERACTION_BUTTONS:
                if trimmed.startswith(btn) or trimmed == btn:
                    return True

        return False
