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
