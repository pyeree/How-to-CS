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
    m = re.search(r"MANUAL:START.*?-->(.*?)<!--.*?MANUAL:END", text, re.S)
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
    due = [n for n in notes if n["review_date"] and n["review_date"] <= iso and n["status"] != "안함"]
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
    g4 = [n for n in notes if n["status"] in ("완료", "복습")]
    if g4:
        return _pick_one(g4, today), "장기복습"
    return None, None


def github_url(folder, filename, repo, branch="main"):
    path = urllib.parse.quote(f"{folder}/{filename}")
    return f"https://github.com/{repo}/blob/{branch}/{path}"


def build_message(note, reason, today_iso, url):
    """텔레그램 MarkdownV2 액티브 리콜 카드."""
    e = md_v2_escape
    flags = ("⭐" if note["priority"] == 1 else "") + ("🔁" if reason in ("복습", "장기복습") else "")
    summary = note["summary"] or note["body_first"]
    summary = summary[:600]
    lines = [
        f"🗓 오늘의 개념 · {e(note['category'])}  {flags}".rstrip(),
        "",
        f"*{e(note['title'])}*",
        "",
        e("30초 안에 설명해보세요  막히면 아래 펼치기"),
    ]
    if summary:
        lines += ["", f"||{e(summary)}||"]
    if not note["summary"]:
        lines += ["", e("아직 30초 요약 없음 → 학습루프 1번 채우기 프롬프트로 작성")]
    lines += ["", f"[{e('노트 열기 (GitHub)')}]({url})"]
    return "\n".join(lines)


def render_note(note, reason, today_iso, url):
    """00_INDEX/🗓 오늘의 개념.md 본문(옵시디언 마크다운)."""
    flags = ("⭐" if note["priority"] == 1 else "") + ("🔁" if reason in ("복습", "장기복습") else "")
    if note["summary"]:
        summary = note["summary"]
    elif note["body_first"]:
        summary = (note["body_first"] +
                   "\n\n> ⓘ 아직 30초 요약 없음 — 노트에서 [[🤖 Claude 학습 루프]] ① 채우기")
    else:
        summary = "> ⓘ 아직 30초 요약 없음 — 노트에서 [[🤖 Claude 학습 루프]] ① 채우기"
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


def load_notes(root):
    """8개 카테고리 + _inbox의 개념 노트(＋ 접두/비.md 제외)를 dict 리스트로."""
    notes = []
    folders = list(CATS) + [("_inbox", "내 노트")]
    for folder, category in folders:
        d = os.path.join(root, folder)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md") or fn.startswith("＋"):
                continue
            try:
                text = open(os.path.join(d, fn), encoding="utf-8").read()
            except OSError:
                continue
            fm = parse_fm(text)
            raw_priority = (fm.get("priority") or "2").strip() or "2"
            try:
                priority = int(raw_priority)
            except ValueError:
                priority = 2
            notes.append({
                "title": fn[:-3],
                "filename": fn,
                "folder": folder,
                "category": category,
                "priority": priority,
                "status": (fm.get("status") or "").strip(),
                "review_date": (fm.get("복습일") or "").strip() or None,
                "summary": extract_summary(text),
                "related": extract_related(text),
                "body_first": body_first(text),
            })
    return notes


def send_telegram(token, chat_id, text):
    """best-effort 발송. 성공 True / 실패 False(예외 삼킴)."""
    api = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id, "text": text,
        "parse_mode": "MarkdownV2", "disable_web_page_preview": "true",
    }).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(api, data=data), timeout=15) as r:
            return r.status == 200
    except Exception as ex:
        print("telegram error:", ex)
        return False


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")  # cp949 콘솔에서 미리보기 이모지 크래시 차단
    dry = "--dry-run" in argv
    dpart = [a for a in argv if a.startswith("--date=")]
    today = date.fromisoformat(dpart[0].split("=", 1)[1]) if dpart else date.today()
    repo = os.environ.get("GITHUB_REPOSITORY", REPO_DEFAULT)

    notes = load_notes(ROOT)
    note, reason = pick_today(notes, today)
    if note is None:
        print("no candidate today")
        return

    url = github_url(note["folder"], note["filename"], repo)
    message = build_message(note, reason, today.isoformat(), url)

    if dry:
        print("PICK:", note["folder"], "/", note["filename"], "/ reason:", reason)
        print("----- TELEGRAM PREVIEW -----")
        print(message)
        return

    note_md = render_note(note, reason, today.isoformat(), url)
    out = os.path.join(ROOT, "00_INDEX", "🗓 오늘의 개념.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(note_md)
    print("wrote:", out)

    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        print("telegram sent" if send_telegram(token, chat, message) else "telegram failed (non-fatal)")
    else:
        print("telegram secrets missing - skip send")


if __name__ == "__main__":
    main(sys.argv[1:])
