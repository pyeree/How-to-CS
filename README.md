# How-to-CS

> **CS 면접 지식을, 빌드 가능한 옵시디언 그래프 vault로 운영하는 학습 시스템.**

찾아서 외우는 게 아니라, **모르는 게 생길 때마다 지도에 한 칸씩 채우는** 방식으로 CS를 공부한다. 지식은 [gyoogle/tech-interview-for-developer](https://github.com/gyoogle/tech-interview-for-developer)에서 가져와 8개 카테고리 그래프로 가공하고, 그 위에 진도·복습·면접 요약 같은 "학습 운영" 레이어를 얹는다.

---

## 🧭 이게 뭔가 — 3겹 구조

| 겹 | 정체 | 누가 만드나 | 손대도 되나 |
|---|---|---|---|
| **지식층** | gyoogle 원본 → 8개 카테고리 위키링크 노트 | `convert.py` | ❌ 빌드가 재생성 (직접 수정 금지) |
| **운영층** | 진도 대시보드 · 학습 로드맵 · 카테고리 지도(MOC) · 템플릿 | `build_index.py` | ❌ 빌드가 재생성 (생성기를 고쳐라) |
| **사람층** | `🎤 30초 요약`, `복습일`, 직접 만든 노트 | **사람 + Claude** | ✅ `🔒 MANUAL` 블록 · `_inbox/`로 **보존됨** |

### 설계 철학 3가지
1. **"검색"이 아니라 "지도 채우기"** — 노트는 지도, Claude는 채우고 시험 보는 파트너.
2. **생성기가 진실의 원천(SSOT)** — 산출물(`.md`)은 언제든 재생성. 그러니 **출력물이 아니라 `_build/`의 스크립트를 고친다.**
3. **사람이 쓴 것은 절대 안 지운다** — 빌드를 100번 돌려도 `🔒 MANUAL` 블록과 `_inbox/`는 살아남는다.

---

## 🚀 5분 시작 (처음이라면 여기부터)

```bash
# 1) 클론
git clone https://github.com/pyeree/How-to-CS.git
cd How-to-CS

# 2) 빌드 — 이거 하나면 끝. (_source가 없으면 gyoogle 원본을 자동으로 받아온다)
python _build/build.py

# 3) Obsidian에서 이 폴더를 vault로 열기
#    설정 → 커뮤니티 플러그인 → Dataview 설치·활성화 (대시보드 자동집계에 필요)
```

열고 나면 `00_INDEX/🏠 Home`에서 출발한다. 의존성 없음(파이썬 표준 라이브러리 + git만 필요).

---

## 🔁 일상 사용 루프

1. **고르기** — `📊 진도 대시보드`의 *🎯 다음에 볼 것*에서 빈출(🔴 priority 1) 주제 하나.
2. **채우기** — 노트 하단 `🎤 면접 30초 요약` 칸을 `🤖 Claude 학습 루프`의 **①채우기** 프롬프트로 채운다 (본문 밖 사실 금지).
3. **표시** — frontmatter `status`를 `완료`로, `복습일`에 *오늘+3일* 날짜 기입.
4. **시험** — 그날 *⏰ 오늘 복습할 것*으로 소환되면, 노트만 보고 **②출제자 모드**로 셀프 시험. 막힌 곳만 보강.

> `status`: `안함 → 공부중 → 완료 → 복습` · `priority`: `1`(🔴빈출) `2`(🟡중요) `3`(🟢심화)

Claude 활용 프롬프트 4종(채우기·출제자·꼬리질문·연결찾기)은 vault 안 **`🤖 Claude 학습 루프`** 노트에 복붙용으로 들어 있다.

---

## 🗂 폴더 구조

```
How-to-CS/
├─ 00_INDEX/          # 🏠 Home · 📊 진도 대시보드 · 🗺️ 학습 로드맵 · 🤖 Claude 학습 루프  (생성물)
├─ 01_운영체제 … 08_소프트웨어공학/   # 카테고리별 개념 노트 + ＋지도(MOC)               (생성물)
├─ _inbox/            # 🗃 직접 만든 내 노트 — 빌드가 절대 안 지우는 안전지대          (내 것)
├─ _templates/        # 개념노트 템플릿                                              (생성물)
├─ _build/            # build.py(통합) · convert.py(지식층) · build_index.py(운영층)
├─ _source/           # gyoogle 원본 클론 — git 추적 제외, 빌드가 자동 관리           (자동)
└─ docs/specs/        # 설계 문서
```

---

## 🛠 빌드 / 재생성 규칙

- **항상 `python _build/build.py` 하나로 돌린다.** (`convert.py`만 단독 실행하면 MOC가 지워진 채 남는다 — 래퍼가 `convert → build_index` 순서를 보장)
- 개별 실행이 필요하면 반드시 이 순서: `python _build/convert.py` → `python _build/build_index.py`.
- **대시보드·로드맵·템플릿 문구를 바꾸려면** 산출물 `.md`가 아니라 `_build/build_index.py`를 고친다 (안 그러면 다음 빌드에 덮어쓰임).
- `.obsidian` 설정은 **없을 때만** 생성한다 — 직접 설치한 플러그인은 보존된다.

## ⚠️ 하지 말 것 (footgun)

- ❌ `_source/`를 손으로 고치지 마라. 빌드가 재생성한다.
- ❌ 카테고리 폴더(01~08)에 **직접 노트를 만들지 마라.** 다음 빌드의 `rmtree`로 사라진다 → 내 노트는 **`_inbox/`**에.
- ❌ 생성된 노트의 `🔒 MANUAL:START ~ END` **마커를 지우지 마라.** 그 안의 30초 요약이 보존되는 근거다.

---

자세한 설계 의도는 [`docs/specs/`](docs/specs/) 참고. CS 지식 출처: [gyoogle/tech-interview-for-developer](https://github.com/gyoogle/tech-interview-for-developer) (MIT).
