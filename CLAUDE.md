# CLAUDE.md — How-to-CS

이 vault에서 작업하는 Claude를 위한 규칙. 사람용 개요·온보딩은 [README.md](README.md)를 먼저 봐라.

## 정체
CS 면접 지식을 **빌드 가능한 옵시디언 그래프 vault**로 운영하는 학습 시스템. 3겹: **지식층**(gyoogle 원본→`convert.py`로 생성) · **운영층**(대시보드/로드맵/MOC/템플릿→`build_index.py`로 생성) · **사람층**(`🔒 MANUAL` 블록·`_inbox/`, 빌드가 보존).

## 절대 규칙 (어기면 작업물이 사라진다)
1. **생성물을 직접 편집하지 마라. 생성기를 고쳐라.** 다음은 모두 빌드 산출물이라 직접 수정하면 다음 빌드에 증발한다:
   - `01_운영체제`~`08_소프트웨어공학`의 개념 노트 + `＋ …지도.md`(MOC)
   - `00_INDEX/`의 Home·진도 대시보드·학습 로드맵·Claude 학습 루프
   - `_templates/개념노트.md`, `_inbox/＋ 내 노트.md`
   - 문구·쿼리·구조를 바꾸려면 **`_build/build_index.py`**(운영층) 또는 **`_build/convert.py`**(지식층)를 수정한다.
2. **`_source/`를 손대지 마라.** gyoogle 원본 클론이고 git 추적 제외다. `build.py`가 없으면 자동 클론한다.
3. **사람이 쓴 것은 보존 영역 안에만.** 노트의 `<!-- 🔒 MANUAL:START … END -->` 블록과 `_inbox/` 폴더만 빌드를 넘어 살아남는다. 이 마커를 지우거나 옮기지 마라.
4. **사용자가 직접 만든 노트는 `_inbox/`에 둔다.** 카테고리 폴더(01~08)는 `convert.py`가 `rmtree`로 통째 재생성한다.

## 빌드
- **항상 `python _build/build.py`** (convert→build_index 순서 보장). 개별 실행 시 순서는 `convert.py` → `build_index.py`.
- Windows 콘솔(cp949)은 이모지 `print`에서 `UnicodeEncodeError`를 낸다 — 스크립트의 stdout 출력에는 이모지를 쓰지 마라(파일 본문 안의 이모지는 무방).
- **데일리**: `python _build/daily.py`는 `build.py`와 독립(`_source` 불필요). 기존 노트를 읽어 하루 하나 선정 → `00_INDEX/🗓 오늘의 개념.md`(생성물) 갱신 + 텔레그램 발송 + **뽑힌 노트의 status/복습일 자동 진행**(안함→완료+3일, 완료→+7일, 복습→+1일). 생성물·선정·문구·복습 로직 다 `_build/daily.py`에 있다. `--dry-run`은 쓰기·발송 안 함. 시크릿은 GitHub Secrets에만.
- **진도 보존**: `convert.py`가 빌드 전 각 노트의 `status`/`복습일`을 스냅샷→재주입해 보존한다(MANUAL 블록과 동일 방식). 그래서 빌드해도 진도가 초기화되지 않는다.
- 의존성 없음: 파이썬 표준 라이브러리 + `git`만.

## 메커니즘 메모
- 빈출 우선순위: `convert.py`의 `PRIORITY_1/PRIORITY_3` 집합 → frontmatter `priority`. priority 1 노트엔 30초 요약 스캐폴드가 자동 삽입된다.
- 위키링크 자동 연결: `convert.py`의 `ALIASES` + 제목 매칭(`autolink`). 코드/기존 링크는 마스킹 후 치환.
- 대시보드/로드맵 집계 범위 `FROM` = 8개 카테고리 + `_inbox`. MOC 대상 `CATS`에는 `_inbox`를 넣지 않는다(그래야 `rmtree` 대상에서 빠진다).
- `.obsidian` 설정은 **없을 때만** 생성(비파괴) — 사용자가 설치한 플러그인 보존.

## 커밋
- 기본 언어 한국어. 변경 의도가 드러나는 서술형 메시지(이 repo는 접두 규칙 없음).
- 산출물 다수가 함께 바뀌는 게 정상(생성기 한 줄 고치면 노트 수십 개 재생성). 생성기 변경과 그 결과를 같은 커밋에 담는다.
