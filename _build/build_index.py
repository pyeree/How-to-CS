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
> 진도의 판정 근거는 **노트의 `🎤 면접 30초 요약`을 채웠는지 하나뿐**이다. 채우면 데일리가
> `status`를 `완료`로 올린다(직접 찍지 않아도 됨). 아래 숫자는 실제로 요약을 쓴 노트만 센다.

## 🎯 다음에 볼 것 (빈출·아직 안 함)
```dataview
TABLE WITHOUT ID file.link AS 개념, file.folder AS 분류
FROM {FROM}
WHERE status = "안함" AND priority = 1
SORT file.folder ASC
```

## ⏰ 오늘 복습할 것 (복습일 도래)
> 30초 요약을 채우면 `복습일`이 "오늘+3일"로 잡히고 그날 여기로 소환된다. ([[🤖 Claude 학습 루프]] 참고)
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

## ① 채우기 (30초 요약 칸 — 내 말로 채운다)
노트의 `🎤 면접 30초 요약` 칸(🔒 MANUAL 블록)을 채울 때.

> ⚠️ **Claude가 대신 써주면 안 된다.** 이 칸은 `daily.py`의 완료 판정 근거다.
> 남의 문장이 들어가면 cron이 도장 찍던 시절과 똑같이 대시보드가 거짓말을 한다.
```
"<주제>" 노트로 30초 요약을 만들 건데, 네가 쓰지 말고 나한테서 뽑아내 줘.
① 먼저 내가 아무것도 안 보고 설명한다.
② 네가 본문 기준으로 빠진 것·틀린 것만 짚어줘 (답은 아직 주지 말고).
③ 내가 다시 설명하면, 내 표현을 살린 채 군더더기만 잘라 최종본으로 정리해줘.
본문에 없는 사실은 추가 금지. 내가 끝내 못 떠올린 부분은 요약에 넣지 말고 따로 알려줘.
```
> 마지막 줄이 핵심이다. 못 떠올린 걸 요약에 채워 넣으면 구멍이 그대로 덮인다.
> 그건 다음 복습 때 다시 만나야 할 항목이지, 완료 처리할 항목이 아니다.

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
- **`완료`는 손으로 찍지 않는다.** `🎤 면접 30초 요약` 칸을 채우면 데일리가 다음 실행 때
  자동으로 `완료` + `복습일`(오늘+3일)로 올려준다. 요약이 비어 있으면 영원히 `안함`이다.
- 그날 [[📊 진도 대시보드]]의 "⏰ 오늘 복습할 것"에 자동 소환된다.
- 이후 복습은 데일리가 뽑을 때마다 `복습일`을 미룬다(+7일). 막히면 `status`를 `복습`으로
  바꾸면 간격이 짧아진다(+1일).

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
