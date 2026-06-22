# -*- coding: utf-8 -*-
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import daily


class TestEscape(unittest.TestCase):
    def test_escapes_markdownv2_specials(self):
        self.assertEqual(daily.md_v2_escape("a-b.c"), "a\\-b\\.c")
        self.assertEqual(daily.md_v2_escape("x_y!"), "x\\_y\\!")

    def test_leaves_korean_and_emoji_untouched(self):
        self.assertEqual(daily.md_v2_escape("뮤텍스 세마포어"), "뮤텍스 세마포어")


if __name__ == "__main__":
    unittest.main()
