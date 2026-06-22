# -*- coding: utf-8 -*-
"""
How-to-CS : 오늘의 개념 데일리
- 기존 노트(8개 카테고리 + _inbox)에서 하루 하나를 복습우선+날짜시드로 선정
- 00_INDEX/🗓 오늘의 개념.md 렌더 + 텔레그램 발송(best-effort)
의존성: 표준 라이브러리만.
"""
import os, re, sys, hashlib, urllib.request, urllib.parse
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = [
    ("01_운영체제", "운영체제"), ("02_네트워크", "네트워크"),
    ("03_데이터베이스", "데이터베이스"), ("04_자료구조", "자료구조"),
    ("05_알고리즘", "알고리즘"), ("06_디자인패턴", "디자인패턴"),
    ("07_컴퓨터구조", "컴퓨터구조"), ("08_소프트웨어공학", "소프트웨어공학"),
]
REPO_DEFAULT = "pyeree/How-to-CS"

_MD_V2 = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")


def md_v2_escape(s):
    """텔레그램 MarkdownV2 특수문자 이스케이프."""
    return _MD_V2.sub(r"\\\1", s or "")


def parse_fm(text):
    """frontmatter를 dict로. (build_index.py와 동일 방식, \\w가 한글 키도 매칭)"""
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"(\w+):\s*(.*)", line)
            if mm:
                fm[mm.group(1)] = mm.group(2).strip()
    return fm


def extract_summary(text):
    """🔒 MANUAL 블록의 30초 요약 본문만. 헤딩/안내 인용문 제거. 없으면 ''."""
    m = re.search(r"MANUAL:START.*?-->(.*?)<!--\s*🔒\s*MANUAL:END", text, re.S)
    if not m:
        return ""
    block = m.group(1)
    block = re.sub(r"(?m)^#+ .*$", "", block)   # 헤딩 제거
    block = re.sub(r"(?m)^>.*$", "", block)      # 인용 안내문 제거
    return block.strip()


def extract_related(text):
    """'## 관련 개념' 섹션 본문(다음 헤딩/MANUAL 전까지). 없으면 ''."""
    m = re.search(r"(?m)^#+ 관련 개념\s*\n(.*?)(?=\n#+ |\n<!--|\Z)", text, re.S)
    return m.group(1).strip() if m else ""


def body_first(text):
    """frontmatter 제거 후 첫 '진짜' 문단(헤딩/인용/코드/주석/구분선 제외)."""
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p[0] in "#>" or p.startswith(("<!--", "---", "```")):
            continue
        return p
    return ""


def _seed(today):
    return int(hashlib.sha1(today.isoformat().encode("utf-8")).hexdigest(), 16)


def _pick_one(cands, today):
    """폴더+파일명 정렬로 결정성 확보 후 날짜시드로 택1."""
    cands = sorted(cands, key=lambda n: (n["folder"], n["filename"]))
    return cands[_seed(today) % len(cands)]


def pick_today(notes, today):
    """복습우선 선정. 반환 (note|None, reason|None)."""
    iso = today.isoformat()
    due = [n for n in notes if n["review_date"] and n["review_date"] <= iso]
    if due:
        earliest = min(n["review_date"] for n in due)
        tied = [n for n in due if n["review_date"] == earliest]
        return _pick_one(tied, today), "복습"
    g2 = [n for n in notes if n["priority"] == 1 and n["status"] == "안함"]
    if g2:
        return _pick_one(g2, today), "빈출신규"
    g3 = [n for n in notes if n["status"] == "안함"]
    if g3:
        return _pick_one(g3, today), "신규"
    g4 = [n for n in notes if n["status"] == "완료"]
    if g4:
        return _pick_one(g4, today), "장기복습"
    return None, None


def github_url(folder, filename, repo, branch="main"):
    path = urllib.parse.quote(f"{folder}/{filename}")
    return f"https://github.com/{repo}/blob/{branch}/{path}"


def build_message(note, reason, today_iso, url):
    """텔레그램 MarkdownV2 액티브 리콜 카드."""
    e = md_v2_escape
    flags = ("⭐" if note["priority"] == 1 else "") + ("🔁" if reason == "복습" else "")
    summary = note["summary"] or note["body_first"]
    summary = summary[:600]
    lines = [
        f"🗓 오늘의 개념 · {e(note['category'])}  {flags}".rstrip(),
        "",
        f"*{e(note['title'])}*",
        "",
        e("30초 안에 설명해보세요  막히면 아래 펼치기"),
        "",
        f"||{e(summary)}||",
    ]
    if not note["summary"]:
        lines += ["", e("아직 30초 요약 없음 → 학습루프 1번 채우기 프롬프트로 작성")]
    lines += ["", f"[{e('노트 열기 (GitHub)')}]({url})"]
    return "\n".join(lines)


def render_note(note, reason, today_iso, url):
    """00_INDEX/🗓 오늘의 개념.md 본문(옵시디언 마크다운)."""
    flags = ("⭐" if note["priority"] == 1 else "") + ("🔁" if reason == "복습" else "")
    if note["summary"]:
        summary = note["summary"]
    else:
        summary = (note["body_first"] +
                   "\n\n> ⓘ 아직 30초 요약 없음 — 노트에서 [[🤖 Claude 학습 루프]] ① 채우기")
    related = note["related"] or "- (관련 개념 없음)"
    return (
        f"# 🗓 오늘의 개념 ({today_iso})\n"
        f"> 매일 daily.py가 갱신하는 생성물. 직접 고치지 마세요.\n\n"
        f"## {note['title']}  · {note['category']} {flags}\n"
        f"[[{note['title']}]] 열기 · [GitHub]({url})\n\n"
        f"👉 먼저 30초로 떠올려보고, 아래 요약과 맞춰보세요.\n\n"
        f"### 🎤 30초 요약\n{summary}\n\n"
        f"### 🔗 관련 개념\n{related}\n\n"
        f"### 🤖 더 훈련하기\n"
        f"[[🤖 Claude 학습 루프]] ② 출제 / ③ 꼬리질문 프롬프트를 돌려보세요.\n\n"
        f"← [[🏠 Home]]\n"
    )
