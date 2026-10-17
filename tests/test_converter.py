import unittest
from clean_pdf2md.presets import get_preset, WeChatPreset, ZhihuPreset, GenericPreset
from clean_pdf2md.converter import CleanPDFConverter

class TestCleanPDF2MD(unittest.TestCase):
    def test_presets_loading(self):
        p_wechat = get_preset("wechat")
        self.assertIsInstance(p_wechat, WeChatPreset)

        p_zhihu = get_preset("zhihu")
        self.assertIsInstance(p_zhihu, ZhihuPreset)

        p_generic = get_preset("generic")
        self.assertIsInstance(p_generic, GenericPreset)

    def test_wechat_noise_filter(self):
        p = WeChatPreset()
        # Page 1 header noise
        self.assertTrue(p.should_filter_header("原创", 0))
        self.assertTrue(p.should_filter_header("阅读原文", 0))
        self.assertTrue(p.should_filter_header("2026年7月19日", 0))
        self.assertTrue(p.should_filter_header("山东", 0))
        self.assertFalse(p.should_filter_header("正常正文标题", 0))

        # Cutoff triggers
        self.assertTrue(p.is_content_cutoff("写留言", 5))
        self.assertTrue(p.is_content_cutoff("精选留言", 10))
        self.assertFalse(p.is_content_cutoff("这是一篇关于在看大模型思考的技术长文", 1))

    def test_converter_init(self):
        converter = CleanPDFConverter(preset="wechat")
        self.assertEqual(converter.preset.name, "wechat")
        self.assertEqual(converter.min_width, 250)

if __name__ == "__main__":
    unittest.main()
