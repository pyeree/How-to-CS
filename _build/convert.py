# -*- coding: utf-8 -*-
"""
How-to-CS : gyoogle 코어 CS 자료 -> Obsidian 위키링크 그래프 vault 변환 (A단계)
- 8개 카테고리 폴더로 분류
- frontmatter(status/priority/tags/aliases/출처) 주입
- 노트 제목/별칭 기반 위키링크 자동 삽입 (실제 존재하는 노트끼리만 연결)
- 기존 상대경로 .md 링크 -> [[ ]] 변환
재실행 가능: dest 폴더를 비우고 다시 생성한다.
"""
import os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # How-to-CS/
SRC = os.path.join(ROOT, "_source")

# (소스 상대폴더, dest 폴더, 태그)
FOLDER_MAP = [
    ("Computer Science/Operating System", "01_운영체제", "운영체제"),
    ("Computer Science/Network",          "02_네트워크", "네트워크"),
    ("Computer Science/Database",         "03_데이터베이스", "데이터베이스"),
    ("Computer Science/Data Structure",   "04_자료구조", "자료구조"),
    ("Algorithm",                         "05_알고리즘", "알고리즘"),
    ("Design Pattern",                    "06_디자인패턴", "디자인패턴"),
    ("Computer Science/Computer Architecture", "07_컴퓨터구조", "컴퓨터구조"),
    ("Computer Science/Software Engineering",  "08_소프트웨어공학", "소프트웨어공학"),
]

# 임포트 제외 (README/메타/취준 가이드)
SKIP_BASENAMES = {
    "README", "프로 준비법", "SAMSUNG Software PRO등급 준비",
}

# 제목 정리: 대괄호 태그 처리
def clean_title(basename):  # basename: 확장자 없는 파일명
    t = basename
    t = re.sub(r"^\[DB\]\s*", "DB ", t)
    t = re.sub(r"^\[Database SQL\]\s*", "SQL ", t)
    t = re.sub(r"^\[Network\]\s*", "", t)
    t = re.sub(r"^\[OS\]\s*", "", t)
    t = re.sub(r"^\[Design Pattern\]\s*", "Design Pattern ", t)
    return t.strip()

# 면접 빈도 우선순위 (cleaned title 기준). 기본 2.
PRIORITY_1 = {
    "Process vs Thread", "PCB & Context Switcing", "DeadLock", "CPU Scheduling",
    "Memory", "Paging and Segmentation", "Semaphore & Mutex",
    "TCP 3 way handshake & 4 way handshake", "HTTP & HTTPS", "TCP (흐름제어혼잡제어)",
    "OSI 7 계층", "UDP",
    "DB Index", "Transaction", "정규화(Normalization)", "Transaction Isolation Level",
    "SQL JOIN", "DB Key", "DB Anomaly",
    "Hash", "Tree", "B Tree & B+ Tree", "Stack & Queue",
    "Array vs ArrayList vs LinkedList", "Linked List", "Binary Search Tree", "Heap",
    "QuickSort", "MergeSort", "DFS & BFS", "동적 계획법 (Dynamic Programming)", "Binary Search",
    "Singleton Pattern", "SOLID", "Observer pattern", "Design Pattern_Factory Method",
    "캐시 메모리(Cache Memory)", "중앙처리장치(CPU) 작동 원리",
    "Object-Oriented Programming",
}
PRIORITY_3 = {
    "비트마스크(BitMask)", "LCA(Lowest Common Ancestor)", "LIS (Longest Increasing Sequence)",
    "Sort_Radix", "Sort_Counting", "간단하지만 알면 좋은 최적화들",
    "최대공약수 & 최소공배수", "Hash Table 구현하기",
    "ARM 프로세서", "패리티 비트 & 해밍 코드", "명령어 Cycle",
    "써드파티(3rd party)란", "애자일(Agile)2", "데브옵스(DevOps)",
    "저장 프로시저(Stored PROCEDURE)", "Redis", "SQL Injection",
    "Composite Pattern", "Adapter Pattern", "Design Pattern_Adapter",
    "Design Pattern_Template Method", "Template Method Pattern", "Strategy Pattern",
    "Design Pattern Overview",
}

# 위키링크용 별칭 사전: canonical title -> [별칭들]
ALIASES = {
    "Process vs Thread": ["프로세스", "스레드", "쓰레드", "Process", "Thread"],
    "PCB & Context Switcing": ["컨텍스트 스위칭", "Context Switching", "PCB"],
    "DeadLock": ["데드락", "교착상태", "DeadLock"],
    "CPU Scheduling": ["CPU 스케줄링", "스케줄링"],
    "Semaphore & Mutex": ["세마포어", "뮤텍스", "Semaphore", "Mutex"],
    "Paging and Segmentation": ["페이징", "세그멘테이션", "Paging"],
    "Memory": ["가상 메모리", "가상메모리"],
    "Race Condition": ["레이스 컨디션", "경쟁 상태", "Race Condition"],
    "Interrupt": ["인터럽트", "Interrupt"],
    "IPC(Inter Process Communication)": ["IPC"],
    "TCP 3 way handshake & 4 way handshake": ["3-way handshake", "3 way handshake", "핸드셰이크"],
    "HTTP & HTTPS": ["HTTPS", "HTTP"],
    "UDP": ["UDP"],
    "OSI 7 계층": ["OSI 7 계층", "OSI 7계층", "OSI"],
    "DNS": ["DNS"],
    "TLS HandShake": ["TLS"],
    "대칭키 & 공개키": ["대칭키", "공개키", "비대칭키"],
    "로드 밸런싱(Load Balancing)": ["로드 밸런싱", "로드밸런싱", "Load Balancing"],
    "DB Index": ["인덱스"],
    "Transaction": ["트랜잭션", "Transaction"],
    "Transaction Isolation Level": ["격리 수준", "Isolation Level"],
    "정규화(Normalization)": ["정규화", "Normalization"],
    "SQL JOIN": ["조인"],
    "SQL과 NOSQL의 차이": ["NoSQL", "NOSQL"],
    "Redis": ["레디스", "Redis"],
    "Hash": ["해시"],
    "B Tree & B+ Tree": ["B+ 트리", "B-Tree", "B+Tree"],
    "Stack & Queue": ["스택"],
    "Heap": ["힙"],
    "Linked List": ["연결 리스트", "링크드 리스트", "Linked List"],
    "QuickSort": ["퀵 정렬", "퀵소트", "QuickSort"],
    "MergeSort": ["병합 정렬", "머지소트", "MergeSort"],
    "DFS & BFS": ["DFS", "BFS"],
    "동적 계획법 (Dynamic Programming)": ["동적 계획법", "Dynamic Programming", "다이나믹 프로그래밍"],
    "Binary Search": ["이진 탐색", "이분 탐색"],
    "다익스트라(Dijkstra)": ["다익스트라", "Dijkstra"],
    "Singleton Pattern": ["싱글톤", "Singleton"],
    "SOLID": ["SOLID"],
    "Observer pattern": ["옵저버 패턴", "Observer"],
    "Design Pattern_Factory Method": ["팩토리 메서드", "팩토리 패턴"],
    "캐시 메모리(Cache Memory)": ["캐시 메모리"],
    "Object-Oriented Programming": ["객체지향", "객체 지향", "OOP"],
}

def get_priority(title):
    if title in PRIORITY_1: return 1
    if title in PRIORITY_3: return 3
    return 2

# ---- 수동 영역(빌드해도 안 지워지는 블록) ----
MANUAL_START = "<!-- 🔒 MANUAL:START — 빌드해도 안 지워짐. 30초 요약 등 직접 작성 -->"
MANUAL_END   = "<!-- 🔒 MANUAL:END -->"
MANUAL_RE = re.compile(re.escape(MANUAL_START) + r".*?" + re.escape(MANUAL_END), re.S)

def extract_manual(text):
    m = MANUAL_RE.search(text)
    return m.group(0) if m else None

def scaffold_manual():
    return (MANUAL_START + "\n## 🎤 면접 30초 요약\n"
            "> 본문을 30초 분량으로 압축. 막히면 [[🤖 Claude 학습 루프]]의 '채우기' 프롬프트 사용.\n\n"
            + MANUAL_END)

# 빌드 전: 기존 노트에서 MANUAL 블록을 스냅샷 (파일명 stem -> 블록)
def snapshot_manual():
    saved = {}
    for _, dest, _ in FOLDER_MAP:
        p = os.path.join(ROOT, dest)
        if not os.path.isdir(p):
            continue
        for fn in os.listdir(p):
            if not fn.endswith(".md"):
                continue
            blk = extract_manual(open(os.path.join(p, fn), encoding="utf-8").read())
            if blk:
                saved[fn[:-3]] = blk
    return saved

# ---- 1단계: 임포트할 파일 수집 + 제목 레지스트리 구축 ----
def collect():
    files = []  # (src_path, dest_folder, tag, title)
    titles = set()
    for sub, dest, tag in FOLDER_MAP:
        d = os.path.join(SRC, sub)
        if not os.path.isdir(d): continue
        for fn in os.listdir(d):
            if not fn.endswith(".md"): continue
            base = fn[:-3]
            if base in SKIP_BASENAMES: continue
            title = clean_title(base)
            files.append((os.path.join(d, fn), dest, tag, title))
            titles.add(title)
    return files, titles

# ---- 위키링크: 코드/링크 마스킹 후 별칭 치환 ----
def autolink(body, self_title, titles):
    # 별칭 후보: (별칭, canonical) — self 제외, canonical이 실제 노트일 때만
    cand = []
    for canon, al in ALIASES.items():
        if canon == self_title or canon not in titles:
            continue
        for a in al:
            cand.append((a, canon))
    # 노트 제목 자체도 별칭으로 (제목이 본문에 그대로 등장하면 링크)
    for t in titles:
        if t != self_title and len(t) >= 4:
            cand.append((t, t))
    # 긴 별칭 우선
    cand.sort(key=lambda x: len(x[0]), reverse=True)

    # 마스킹: 코드펜스, 인라인코드, 기존 위키링크, 기존 md링크
    masks = []
    def mask(m):
        masks.append(m.group(0))
        return f"\x00{len(masks)-1}\x00"
    body = re.sub(r"```.*?```", mask, body, flags=re.S)
    body = re.sub(r"`[^`]*`", mask, body)
    body = re.sub(r"\[\[.*?\]\]", mask, body)
    body = re.sub(r"\[[^\]]*\]\([^)]*\)", mask, body)

    linked = set()
    for alias, canon in cand:
        if canon in linked:
            continue
        # ASCII 별칭은 단어경계, 한글은 그대로 substring
        if re.fullmatch(r"[A-Za-z0-9 +\-]+", alias):
            pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])")
        else:
            pat = re.compile(re.escape(alias))
        m = pat.search(body)
        if not m:
            continue
        # placeholder(\x00..\x00) 내부면 skip
        if "\x00" in m.group(0):
            continue
        repl = f"[[{canon}]]" if alias == canon else f"[[{canon}|{alias}]]"
        body = body[:m.start()] + repl + body[m.end():]
        linked.add(canon)

    # 마스크 복원
    for i in range(len(masks) - 1, -1, -1):
        body = body.replace(f"\x00{i}\x00", masks[i])
    return body

# 기존 상대경로 .md 링크 -> [[ ]]
def convert_mdlinks(body, titles):
    def repl(m):
        text, target = m.group(1), m.group(2)
        if not target.lower().endswith(".md"):
            return m.group(0)
        base = os.path.basename(target.replace("%20", " "))
        base = re.sub(r"\.md$", "", base, flags=re.I)
        ct = clean_title(base)
        if ct in titles:
            return f"[[{ct}|{text}]]" if text and text != ct else f"[[{ct}]]"
        return m.group(0)
    return re.sub(r"\[([^\]]*)\]\(([^)]+)\)", repl, body)

def make_frontmatter(title, tag, aliases):
    al = sorted(set(a for a in aliases if a != title), key=str.lower)
    lines = ["---", f"tags: [{tag}]", "status: 안함", f"priority: {get_priority(title)}", "복습일: "]
    if al:
        lines.append("aliases: [" + ", ".join(f'"{a}"' for a in al) + "]")
    lines += ["출처: gyoogle", "---", ""]
    return "\n".join(lines)

def run():
    files, titles = collect()
    # 재생성 전에 수동 영역(30초 요약 등) 스냅샷 -> rmtree 후 재주입
    saved_manual = snapshot_manual()
    # dest 폴더 초기화
    for _, dest, _ in FOLDER_MAP:
        p = os.path.join(ROOT, dest)
        if os.path.isdir(p):
            shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)

    stats = {}
    for src, dest, tag, title in files:
        with open(src, encoding="utf-8") as f:
            raw = f.read()
        # 본문에서 기존 H1 제목 라인은 그대로 두되, frontmatter 별도 부착
        body = raw
        body = convert_mdlinks(body, titles)
        body = autolink(body, title, titles)
        aliases = ALIASES.get(title, [])
        out = make_frontmatter(title, tag, aliases) + body
        # 안전한 파일명 (윈도우 금지문자 제거)
        safe = re.sub(r'[<>:"/\\|?*]', "", title)
        # 수동 영역: 보존본 우선, 없으면 빈출(priority 1)에 빈 스캐폴드
        manual = saved_manual.get(safe)
        if manual is None and get_priority(title) == 1:
            manual = scaffold_manual()
        if manual:
            out = out.rstrip() + "\n\n" + manual + "\n"
        with open(os.path.join(ROOT, dest, safe + ".md"), "w", encoding="utf-8") as f:
            f.write(out)
        stats[dest] = stats.get(dest, 0) + 1

    total = sum(stats.values())
    print(f"변환 완료: 총 {total}개 노트")
    for _, dest, _ in FOLDER_MAP:
        print(f"  {dest}: {stats.get(dest,0)}개")

if __name__ == "__main__":
    run()
