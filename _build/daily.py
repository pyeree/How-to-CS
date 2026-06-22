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
