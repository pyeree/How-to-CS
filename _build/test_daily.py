# -*- coding: utf-8 -*-
import os, sys, unittest
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import daily


class TestEscape(unittest.TestCase):
    def test_escapes_markdownv2_specials(self):
        self.assertEqual(daily.md_v2_escape("a-b.c"), "a\\-b\\.c")
        self.assertEqual(daily.md_v2_escape("x_y!"), "x\\_y\\!")

    def test_leaves_korean_and_emoji_untouched(self):
        self.assertEqual(daily.md_v2_escape("뮤텍스 세마포어"), "뮤텍스 세마포어")


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


class TestMessage(unittest.TestCase):
    TODAY = date(2026, 6, 22)

    def test_github_url_encodes_path(self):
        u = daily.github_url("01_운영체제", "뮤텍스 vs 세마포어.md", "pyeree/How-to-CS")
        self.assertTrue(u.startswith("https://github.com/pyeree/How-to-CS/blob/main/"))
        self.assertNotIn(" ", u)  # 공백 인코딩됨

    def test_build_message_has_title_spoiler_link(self):
        note = _note("뮤텍스 vs 세마포어", priority=1, status="완료", review="2026-06-10")
        note["summary"] = "뮤텍스는 1개를 동기화."
        url = "https://github.com/pyeree/How-to-CS/blob/main/x"
        msg = daily.build_message(note, "복습", self.TODAY.isoformat(), url)
        self.assertIn("오늘의 개념", msg)
        self.assertIn("뮤텍스 vs 세마포어", msg.replace("\\", ""))  # 제목(이스케이프 무시)
        self.assertIn("||", msg)        # 스포일러로 요약 가림
        self.assertIn("⭐", msg)         # 빈출
        self.assertIn("🔁", msg)         # 복습
        self.assertIn(url, msg)         # 링크

    def test_build_message_empty_summary_hint(self):
        note = _note("TCP", priority=2, status="안함")
        note["summary"] = ""
        note["body_first"] = "핸드셰이크 설명"
        msg = daily.build_message(note, "신규", self.TODAY.isoformat(), "http://x")
        self.assertIn("핸드셰이크 설명", msg.replace("\\", ""))
        self.assertIn("채우기", msg)     # 작성 유도 문구


class TestRender(unittest.TestCase):
    def test_render_note_contains_key_parts(self):
        note = _note("뮤텍스 vs 세마포어", priority=1, status="완료", review="2026-06-10")
        note["summary"] = "뮤텍스는 1개."
        note["related"] = "- [[Deadlock]]"
        md = daily.render_note(note, "복습", "2026-06-22", "http://x")
        self.assertIn("# 🗓 오늘의 개념 (2026-06-22)", md)
        self.assertIn("[[뮤텍스 vs 세마포어]]", md)
        self.assertIn("뮤텍스는 1개.", md)
        self.assertIn("[[Deadlock]]", md)
        self.assertIn("[[🤖 Claude 학습 루프]]", md)
        self.assertIn("← [[🏠 Home]]", md)

    def test_render_note_empty_summary_hint(self):
        note = _note("TCP", status="안함")
        note["summary"] = ""
        note["body_first"] = "핸드셰이크 설명"
        md = daily.render_note(note, "신규", "2026-06-22", "http://x")
        self.assertIn("핸드셰이크 설명", md)
        self.assertIn("채우기", md)


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


class TestBuildMessageEmptySpoiler(unittest.TestCase):
    """Test A: Fix 1 / C2 — 빈 스포일러 억제"""
    TODAY = date(2026, 6, 22)

    def test_no_spoiler_when_summary_and_body_first_both_empty(self):
        note = _note("빈노트", priority=2, status="안함")
        note["summary"] = ""
        note["body_first"] = ""
        msg = daily.build_message(note, "신규", self.TODAY.isoformat(), "http://x")
        self.assertNotIn("||", msg)
        self.assertIn("채우기", msg)


class TestPickExcludesAntham(unittest.TestCase):
    """Test B: Fix 5 / I3 — 복습 버킷에서 안함 상태 제외"""
    TODAY = date(2026, 6, 22)

    def test_antham_with_review_date_not_treated_as_review(self):
        notes = [
            _note("복습안함", status="안함", review="2026-06-10"),  # 안함 + 복습일 → 버킷 제외
            _note("신규빈출", priority=1, status="안함"),
        ]
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertEqual(reason, "빈출신규")
        self.assertEqual(picked["title"], "신규빈출")


class TestPickOrphanStatus(unittest.TestCase):
    """Test C: I5 — 진행중 상태만 있을 때 (None, None) 반환"""
    TODAY = date(2026, 6, 22)

    def test_only_jinhengjoong_returns_none(self):
        notes = [
            _note("A", status="진행중"),
            _note("B", status="진행중"),
        ]
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertIsNone(picked)
        self.assertIsNone(reason)


class TestPickBokseupFallback(unittest.TestCase):
    """M2 test: status='복습' + review_date=None -> g4 fallback, reason='장기복습'"""
    TODAY = date(2026, 6, 22)

    def test_bokseup_no_review_date_falls_into_janggi(self):
        notes = [_note("A", status="복습", review=None)]
        picked, reason = daily.pick_today(notes, self.TODAY)
        self.assertIsNotNone(picked)
        self.assertEqual(picked["title"], "A")
        self.assertEqual(reason, "장기복습")


class TestBuildMessageJanggiFlag(unittest.TestCase):
    """M4 test: build_message with reason='장기복습' shows 🔁"""
    TODAY = date(2026, 6, 22)

    def test_janggi_shows_repeat_flag(self):
        note = _note("완료노트", priority=2, status="완료")
        note["summary"] = "요약 있음."
        msg = daily.build_message(note, "장기복습", self.TODAY.isoformat(), "http://x")
        self.assertIn("🔁", msg)


class TestRenderNoteEmptySummaryAndBody(unittest.TestCase):
    """M5 test: render_note with summary='' and body_first='' -> no leading blank before hint"""
    def test_no_blank_line_before_hint_when_both_empty(self):
        note = _note("빈노트", status="안함")
        note["summary"] = ""
        note["body_first"] = ""
        md = daily.render_note(note, "신규", "2026-06-22", "http://x")
        # Find the section after the 30초 요약 header and verify no "\n\n>" immediately follows
        header = "### 🎤 30초 요약\n"
        idx = md.index(header)
        after_header = md[idx + len(header):]
        self.assertFalse(after_header.startswith("\n\n>"), "빈 줄 없이 힌트가 바로 와야 한다")
        self.assertIn("채우기", after_header)


NOTE_LONG_BODY = """---
tags: [네트워크]
status: 안함
priority: 1
---
## TCP 흐름제어

첫 문단 설명입니다.

#### 세부 항목

둘째 문단 설명입니다.

## 관련 개념
- [[혼잡 제어]]

<!-- 🔒 MANUAL:START -->
## 🎤 면접 30초 요약
<!-- 🔒 MANUAL:END -->
"""


class TestBodyExcerpt(unittest.TestCase):
    def test_collects_multiple_paragraphs_until_next_section(self):
        out = daily.body_first(NOTE_LONG_BODY)
        self.assertIn("첫 문단 설명입니다.", out)
        self.assertIn("둘째 문단 설명입니다.", out)   # #### 서브헤딩 건너뛰고 계속 수집
        self.assertNotIn("혼잡 제어", out)            # ## 관련 개념에서 멈춤

    def test_respects_char_limit_with_ellipsis(self):
        long_text = "---\ntags: [x]\n---\n## 제목\n\n" + ("가" * 500)
        out = daily.body_first(long_text, limit=100)
        self.assertLessEqual(len(out), 101)            # 100자 + 말줄임표(…)
        self.assertTrue(out.endswith("…"))

    def test_empty_when_no_body(self):
        self.assertEqual(daily.body_first("---\ntags: [x]\n---\n## 제목만\n"), "")


if __name__ == "__main__":
    unittest.main()
