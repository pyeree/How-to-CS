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
# 대시보드/로드맵 집계 범위 = 8개 카테고리 + _inbox(손수 추가한 내 노트).
# CATS(=MOC/Home 생성 대상)에는 _inbox를 넣지 않아 convert.py의 rmtree 대상에서 제외된다.
FROM = " OR ".join(f'"{d}"' for d, _ in CATS) + ' OR "_inbox"'

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
             "- [[🗓 오늘의 개념]] — 오늘 복습/공부할 단 하나 (매일 갱신)",
             "- [[📊 진도 대시보드]] — 지금 뭐부터 볼지 / 진도율",
             "- [[🗺️ 학습 로드맵]] — Tier 순서 (빈출→심화)",
             "- [[🤖 Claude 학습 루프]] — Claude로 채우고 시험 보는 법", "",
             "## 🗂 카테고리 지도"]
    for folder, tag in CATS:
        lines.append(f"- [[＋ {tag} 지도|{tag}]]")
    lines += ["", "## ⚙️ 처음 한 번 설정",
              "1. Obsidian에서 이 폴더를 vault로 열기",
              "2. 설정 → 커뮤니티 플러그인 → **Dataview** 설치 후 활성화 (대시보드 자동집계에 필요)",
              "3. 그래프 뷰(좌측 ●)를 열면 8개 클러스터가 보임", "",
              "## ✍️ 새 개념 추가법",
              "`_templates/개념노트.md`를 복사해 [[＋ 내 노트|_inbox]] 폴더에 저장하고, "
              "본문에서 `[[ ]]`로 연결하면 그래프에 자동 편입된다. "
              "(카테고리 01~08 폴더는 빌드가 재생성하므로 직접 만든 노트는 [[＋ 내 노트|_inbox]]에 둘 것.)"]
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

## ⏰ 오늘 복습할 것 (복습일 도래)
> `완료`로 바꿀 때 `복습일`에 "오늘+3일"을 적어두면 그날 여기로 소환된다. ([[🤖 Claude 학습 루프]] 참고)
```dataview
TABLE WITHOUT ID file.link AS 개념, 복습일, priority AS 빈도
FROM {FROM}
WHERE 복습일 AND 복습일 <= date(today)
SORT 복습일 ASC
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

<!-- 🔒 MANUAL:START — 빌드해도 안 지워짐. 30초 요약 등 직접 작성 -->
## 🎤 면접 30초 요약
> 본문을 30초 분량으로 압축. 막히면 [[🤖 Claude 학습 루프]]의 '채우기' 프롬프트 사용.

<!-- 🔒 MANUAL:END -->
'''
    with open(os.path.join(d, "개념노트.md"), "w", encoding="utf-8") as f:
        f.write(c)

# ---- Claude 학습 루프 가이드 ----
def build_loop_guide():
    idx = os.path.join(ROOT, "00_INDEX")
    c = '''# 🤖 Claude 학습 루프

> 노트는 "지도", Claude는 "채우고 시험 보는 파트너". 아래 4개 프롬프트를 복붙해서 돌린다.
> 핵심 루프: **모르는 주제 발견 → ① 채우기 → 며칠 뒤 ② 출제로 셀프시험 → 막힌 곳 보강**.

## ① 채우기 (30초 요약 칸 메우기)
노트의 `🎤 면접 30초 요약` 칸(🔒 MANUAL 블록)을 채울 때.
```
이 노트 본문을 바탕으로 '면접 30초 요약'을 5~7문장으로 써줘.
본문에 없는 사실은 절대 추가하지 말고(환각 금지), 면접에서 말하듯 구어체로.
```

## ② 출제자 모드 (셀프 시험)
며칠 뒤, 노트만 보고 답하기.
```
"<주제>" 관련 CS 면접 질문 5개를 내줘. 내가 답하면 핵심 키워드 기준으로 채점하고,
빠뜨린 포인트를 짚어줘. 한 번에 한 문제씩 진행.
```

## ③ 꼬리질문 훈련
면접관이 파고들 후속 질문 미리 받기.
```
"<주제>"로 면접관이 깊게 파고들 만한 꼬리질문 5개와, 각 질문의 모범답변 핵심을 줘.
```

## ④ 연결 찾기 (그래프 엣지 만들기)
같이 물어볼 개념 → 위키링크 후보.
```
"<주제>"와 함께 묶여 나오는 CS 개념을 알려줘.
출력은 반드시 [[개념이름]] 형식 목록으로만. 그대로 노트 '관련 개념'에 붙일 거야.
```

## 🔁 복습 규칙 (대시보드 ⏰ 칸과 연동)
- 노트를 `완료`로 바꿀 때, frontmatter `복습일`에 **오늘+3일** 날짜를 적는다 (예: `복습일: 2026-06-08`).
- 그날 [[📊 진도 대시보드]]의 "⏰ 오늘 복습할 것"에 자동 소환된다.
- 복습해서 잘 되면 `복습일`을 더 미루고(+7일), 막히면 `status`를 `복습`으로.

← [[🏠 Home]]
'''
    with open(os.path.join(idx, "🤖 Claude 학습 루프.md"), "w", encoding="utf-8") as f:
        f.write(c)

# ---- _inbox (손수 만든 내 노트 — 빌드가 절대 안 지우는 안전지대) ----
def build_inbox():
    d = os.path.join(ROOT, "_inbox")
    os.makedirs(d, exist_ok=True)
    # 안내 노트만 재생성(＋ 접두=생성물). 그 외 사용자 노트는 건드리지 않는다.
    guide = '''# 🗃 내 노트 (_inbox)

> **여기는 빌드가 절대 지우지 않는 안전지대다.** `convert.py`는 8개 카테고리 폴더만
> 재생성하므로, gyoogle 원본에 없는 *내가 직접 만든* 개념·정리·면접 회고는 여기에 둔다.

## 쓰는 법
1. `_templates/개념노트.md`를 복사해 이 폴더에 새 노트로 저장.
2. `tags`·`priority`·`status`를 채우면 [[📊 진도 대시보드]]·[[🗺️ 학습 로드맵]]에 함께 집계된다.
3. 본문에서 `[[개념이름]]`으로 기존 노트와 연결하면 그래프에 편입된다.

> 카테고리 폴더(01~08)에 직접 노트를 만들면 다음 빌드 때 사라진다. 내 노트는 반드시 여기에.

← [[🏠 Home]]
'''
    with open(os.path.join(d, "＋ 내 노트.md"), "w", encoding="utf-8") as f:
        f.write(guide)

# ---- .obsidian 설정 (없을 때만 생성 — 사용자가 추가한 플러그인/설정 보존) ----
def build_obsidian():
    d = os.path.join(ROOT, ".obsidian")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "community-plugins.json")
    if not os.path.exists(cp):
        with open(cp, "w", encoding="utf-8") as f:
            f.write('["dataview"]')
    aj = os.path.join(d, "app.json")
    if not os.path.exists(aj):
        with open(aj, "w", encoding="utf-8") as f:
            f.write('{"alwaysUpdateLinks": true, "newFileLocation": "current", '
                    '"userIgnoreFilters": ["_source/", "_build/", "docs/"]}')

def run():
    build_mocs(); build_home(); build_dashboard(); build_roadmap()
    build_template(); build_loop_guide(); build_inbox(); build_obsidian()
    print("INDEX 레이어 생성 완료: MOC 8개 + Home/대시보드/로드맵 + 템플릿 + 학습루프 + _inbox + .obsidian")

if __name__ == "__main__":
    run()
