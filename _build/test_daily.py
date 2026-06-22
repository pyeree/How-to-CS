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


from datetime import date


def _note(title, folder="01_운영체제", priority=2, status="안함", review=None):
    return {"title": title, "filename": title + ".md", "folder": folder,
            "category": "운영체제", "priority": priority, "status": status,
            "review_date": review, "summary": "", "related": "", "body_first": ""}


class TestPick(unittest.TestCase):
    TODAY = date(2026, 6, 22)

    def test_review_due_wins_and_earliest_first(self):
        notes = [
            _note("A", priority=1, status="안함"),
            _note("B", status="완료", review="2026-06-21"),
            _note("C", status="완료", review="2026-06-10"),  # 가장 오래된 복습
        ]
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertEqual(picked["title"], "C")
        self.assertEqual(reason, "복습")

    def test_priority1_new_when_no_review(self):
        notes = [_note("A", priority=2, status="안함"),
                 _note("B", priority=1, status="안함")]
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertEqual(picked["title"], "B")
        self.assertEqual(reason, "빈출신규")

    def test_any_new_when_no_priority1(self):
        notes = [_note("A", priority=2, status="안함"),
                 _note("B", priority=3, status="완료")]
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertEqual(picked["title"], "A")
        self.assertEqual(reason, "신규")

    def test_completed_long_review_fallback(self):
        notes = [_note("A", status="완료"), _note("B", status="복습")]
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertEqual(picked["title"], "A")
        self.assertEqual(reason, "장기복습")

    def test_none_when_empty(self):
        picked, reason = daily.pick_today([], self.TODAY)
        self.assertIsNone(picked)
        self.assertIsNone(reason)

    def test_deterministic_same_date(self):
        notes = [_note(c, priority=1, status="안함") for c in ["A", "B", "C", "D", "E"]]
        p1, _ = daily.pick_today(notes, self.TODAY)
        p2, _ = daily.pick_today(notes, self.TODAY)
        self.assertEqual(p1["title"], p2["title"])  # 같은 날 = 같은 결과

    def test_future_review_not_due(self):
        notes = [_note("A", priority=1, status="안함"),
                 _note("B", status="완료", review="2026-12-31")]  # 미래 = 미도래
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertEqual(reason, "빈출신규")
        self.assertEqual(picked["title"], "A")


NOTE_WITH_SUMMARY = """---
tags: [운영체제]
status: 완료
priority: 1
복습일: 2026-06-20
---
## 뮤텍스 vs 세마포어

본문 첫 문단입니다.

## 관련 개념
- [[Semaphore & Mutex]]
- [[Deadlock]]

<!-- 🔒 MANUAL:START — 빌드해도 안 지워짐. 30초 요약 등 직접 작성 -->
## 🎤 면접 30초 요약
> 본문을 30초 분량으로 압축.

뮤텍스는 1개, 세마포어는 N개를 동기화합니다.
<!-- 🔒 MANUAL:END -->
"""

NOTE_EMPTY_SUMMARY = """---
tags: [네트워크]
status: 안함
priority: 2
복습일:
---
## TCP 3-way handshake

핸드셰이크 본문 첫 문단.

## 관련 개념
- [[TCP/IP]]

<!-- 🔒 MANUAL:START — 빌드해도 안 지워짐. 30초 요약 등 직접 작성 -->
## 🎤 면접 30초 요약
> 본문을 30초 분량으로 압축.

<!-- 🔒 MANUAL:END -->
"""


class TestExtract(unittest.TestCase):
    def test_parse_fm(self):
        fm = daily.parse_fm(NOTE_WITH_SUMMARY)
        self.assertEqual(fm["status"], "완료")
        self.assertEqual(fm["priority"], "1")
        self.assertEqual(fm["복습일"], "2026-06-20")

    def test_parse_fm_empty_review(self):
        fm = daily.parse_fm(NOTE_EMPTY_SUMMARY)
        self.assertEqual(fm.get("복습일", ""), "")

    def test_extract_summary_present(self):
        s = daily.extract_summary(NOTE_WITH_SUMMARY)
        self.assertIn("뮤텍스는 1개", s)
        self.assertNotIn("본문을 30초", s)   # 안내 인용문 제거
        self.assertNotIn("면접 30초 요약", s)  # 헤딩 제거

    def test_extract_summary_empty(self):
        self.assertEqual(daily.extract_summary(NOTE_EMPTY_SUMMARY), "")

    def test_extract_related(self):
        r = daily.extract_related(NOTE_WITH_SUMMARY)
        self.assertIn("[[Semaphore & Mutex]]", r)
        self.assertIn("[[Deadlock]]", r)
        self.assertNotIn("MANUAL", r)

    def test_body_first(self):
        self.assertEqual(daily.body_first(NOTE_EMPTY_SUMMARY), "핸드셰이크 본문 첫 문단.")


if __name__ == "__main__":
    unittest.main()
