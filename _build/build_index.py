# -*- coding: utf-8 -*-
"""
How-to-CS : INDEX 레이어 생성
- 카테고리별 지도(MOC) 노트 (그래프 허브 -> 고립 0)
- 00_INDEX/🏠 Home, 📊 진도 대시보드(Dataview), 🗺️ 학습 로드맵(Dataview)
- _templates/개념노트.md
- .obsidian 최소 설정 (Dataview 활성화)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = [
    ("01_운영체제", "운영체제"), ("02_네트워크", "네트워크"),
    ("03_데이터베이스", "데이터베이스"), ("04_자료구조", "자료구조"),
    ("05_알고리즘", "알고리즘"), ("06_디자인패턴", "디자인패턴"),
    ("07_컴퓨터구조", "컴퓨터구조"), ("08_소프트웨어공학", "소프트웨어공학"),
]
FROM = " OR ".join(f'"{d}"' for d, _ in CATS)

def parse_fm(text):
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"(\w+):\s*(.*)", line)
            if mm:
                fm[mm.group(1)] = mm.group(2).strip()
    return fm

def notes_in(folder):
    d = os.path.join(ROOT, folder)
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md") or fn.startswith("＋"):
            continue
        fm = parse_fm(open(os.path.join(d, fn), encoding="utf-8").read())
        out.append((fn[:-3], int(fm.get("priority", "2") or 2)))
    return out

PRI_ICON = {1: "🔴", 2: "🟡", 3: "🟢"}

# ---- 카테고리 MOC (각 폴더 안, ＋ 접두로 최상단 정렬) ----
def build_mocs():
    for folder, tag in CATS:
        ns = notes_in(folder)
        ns.sort(key=lambda x: (x[1], x[0]))  # 우선순위 -> 이름
        lines = [f"# 🗂 {tag} 지도", "",
                 f"> `{tag}` 카테고리의 모든 개념. 🔴빈출 🟡중요 🟢심화", "",
                 "```dataview",
                 'TABLE WITHOUT ID file.link AS 개념, status AS 상태, priority AS 빈도',
                 f'FROM "{folder}"',
                 'WHERE file.name != this.file.name',
                 "SORT priority ASC, file.name ASC", "```", "",
                 "---", "", "### 전체 목록 (플러그인 없이도 보임)", ""]
        for title, pri in ns:
            lines.append(f"- {PRI_ICON.get(pri,'🟡')} [[{title}]]")
        lines += ["", "← [[🏠 Home]]"]
        with open(os.path.join(ROOT, folder, f"＋ {tag} 지도.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

# ---- Home ----
def build_home():
    idx = os.path.join(ROOT, "00_INDEX")
    os.makedirs(idx, exist_ok=True)
    lines = ["# 🏠 How-to-CS", "",
             "> 임현우의 CS 지식 그래프. 면접 빈도 우선으로 공부하고, 그래프로 연결한다.", "",
             "## 🚀 바로가기",
             "- [[📊 진도 대시보드]] — 지금 뭐부터 볼지 / 진도율",
             "- [[🗺️ 학습 로드맵]] — Tier 순서 (빈출→심화)", "",
             "## 🗂 카테고리 지도"]
    for folder, tag in CATS:
        lines.append(f"- [[＋ {tag} 지도|{tag}]]")
    lines += ["", "## ⚙️ 처음 한 번 설정",
              "1. Obsidian에서 이 폴더를 vault로 열기",
              "2. 설정 → 커뮤니티 플러그인 → **Dataview** 설치 후 활성화 (대시보드 자동집계에 필요)",
              "3. 그래프 뷰(좌측 ●)를 열면 8개 클러스터가 보임", "",
              "## ✍️ 새 개념 추가법",
              "`_templates/개념노트.md`를 복사해서 해당 카테고리 폴더에 넣고, "
              "본문에 다른 개념을 `[[ ]]`로 연결하면 그래프에 자동 편입된다."]
    with open(os.path.join(idx, "🏠 Home.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ---- 대시보드 ----
def build_dashboard():
    idx = os.path.join(ROOT, "00_INDEX")
    c = f'''# 📊 진도 대시보드

> ⚠️ 이 페이지는 **Dataview 플러그인**이 있어야 자동집계됩니다. ([[🏠 Home]] 설정 참고)
> 공부 상태는 각 노트 상단 `status` 값을 바꾸면 자동 반영: **안함 → 공부중 → 완료 → 복습**

## 🎯 다음에 볼 것 (빈출·아직 안 함)
```dataview
TABLE WITHOUT ID file.link AS 개념, file.folder AS 분류
FROM {FROM}
WHERE status = "안함" AND priority = 1
SORT file.folder ASC
```

## 📖 지금 공부 중
```dataview
LIST FROM {FROM}
WHERE status = "공부중"
```

## 🔁 복습 대상
```dataview
LIST FROM {FROM}
WHERE status = "복습"
```

## 📈 분류별 진도율
```dataview
TABLE WITHOUT ID
  rows.file.folder[0] AS 분류,
  length(filter(rows, (r) => r.status = "완료")) AS 완료,
  length(rows) AS 전체,
  round(100 * length(filter(rows, (r) => r.status = "완료")) / length(rows)) + "%" AS 달성률
FROM {FROM}
GROUP BY file.folder
SORT 분류 ASC
```

## 🧮 전체 요약
```dataview
TABLE WITHOUT ID
  length(rows) AS 전체,
  length(filter(rows, (r) => r.status = "완료")) AS 완료,
  length(filter(rows, (r) => r.status = "공부중")) AS 공부중,
  length(filter(rows, (r) => r.status = "안함")) AS 안함
FROM {FROM}
GROUP BY true
```

← [[🏠 Home]]
'''
    with open(os.path.join(idx, "📊 진도 대시보드.md"), "w", encoding="utf-8") as f:
        f.write(c)

# ---- 로드맵 ----
def build_roadmap():
    idx = os.path.join(ROOT, "00_INDEX")
    c = f'''# 🗺️ 학습 로드맵

> 면접 빈도 우선. **Tier 1(🔴 빈출)부터** 끝내고 2→3으로. 상태는 노트의 `status`로 관리.

## 🔴 Tier 1 — 빈출 (가장 먼저)
```dataview
TABLE WITHOUT ID file.link AS 개념, file.folder AS 분류, status AS 상태
FROM {FROM}
WHERE priority = 1
SORT status ASC, file.folder ASC
```

## 🟡 Tier 2 — 중요
```dataview
TABLE WITHOUT ID file.link AS 개념, file.folder AS 분류, status AS 상태
FROM {FROM}
WHERE priority = 2
SORT file.folder ASC
```

## 🟢 Tier 3 — 심화
```dataview
TABLE WITHOUT ID file.link AS 개념, file.folder AS 분류, status AS 상태
FROM {FROM}
WHERE priority = 3
SORT file.folder ASC
```

← [[🏠 Home]]
'''
    with open(os.path.join(idx, "🗺️ 학습 로드맵.md"), "w", encoding="utf-8") as f:
        f.write(c)

# ---- 템플릿 ----
def build_template():
    d = os.path.join(ROOT, "_templates")
    os.makedirs(d, exist_ok=True)
    c = '''---
tags: [카테고리명]
status: 안함
priority: 2
복습일:
출처:
---
# 개념 이름

## 한 줄 정의

## 핵심 내용

## 관련 개념
- [[연결할 개념]]

## 면접 포인트 / 한마디
'''
    with open(os.path.join(d, "개념노트.md"), "w", encoding="utf-8") as f:
        f.write(c)

# ---- .obsidian 설정 ----
def build_obsidian():
    d = os.path.join(ROOT, ".obsidian")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "community-plugins.json"), "w", encoding="utf-8") as f:
        f.write('["dataview"]')
    with open(os.path.join(d, "app.json"), "w", encoding="utf-8") as f:
        f.write('{"alwaysUpdateLinks": true, "newFileLocation": "current", '
                '"userIgnoreFilters": ["_source/", "_build/", "docs/"]}')

def run():
    build_mocs(); build_home(); build_dashboard(); build_roadmap()
    build_template(); build_obsidian()
    print("INDEX 레이어 생성 완료: MOC 8개 + Home/대시보드/로드맵 + 템플릿 + .obsidian")

if __name__ == "__main__":
    run()
