---
tags: [네트워크]
status: 완료
priority: 1
복습일: 2026-06-26
aliases: ["WAF", "Web Application Firewall", "웹 방화벽", "웹방화벽", "False Positive", "오탐"]
출처: 직접 작성 (실경험 트러블슈팅 + [[SQL Injection]] 연계)
---
## 웹 방화벽(WAF, Web Application Firewall)

> **애플리케이션 계층(OSI 7계층)에서 HTTP/HTTPS 트래픽을 검사해 악의적인 요청을 차단하는 보안 장비.** 일반 방화벽이 IP·포트(L3/L4)를 본다면, WAF는 요청 **본문·파라미터의 내용**을 본다.

클라이언트와 웹 서버(WAS) 사이에 위치해, 요청이 서버에 닿기 **전에** 검사한다. 주 방어 대상은 [[SQL Injection]], XSS, 경로 조작 같은 웹 애플리케이션 공격이다.

```
사용자 → [WAF: 요청 내용 검사] → WAS/DB
              └ 위험 패턴이면 차단(Drop/Block)
```

<br>

#### 1. 탐지 원리

----

- **시그니처 매칭 (Signature / 패턴 매칭)**: 알려진 공격 패턴 DB를 기준으로 입력값을 검사한다. 예) `SELECT`, `UPDATE`, `WHERE`, `--`(주석), `' OR '1'='1'` 같은 SQL 키워드·특수문자 조합.
- **정규표현식(Regex) 검사**: 일정 규칙을 가진 문자열이 SQL/스크립트 구문 형태인지 필터링한다.

> 핵심: WAF는 **"공격 의도"가 아니라 "패턴"** 을 본다. → 의도가 없어도 패턴이 걸리면 막힌다(=오탐).

<br>

#### 2. 오탐(False Positive) — 실제 겪은 케이스

----

공격이 아닌 **정상 텍스트**(개발 일지, 학술 보고서, 소스코드 본문)에 SQL 구문이 들어가면 WAF가 공격으로 **오인 차단**한다.

**실경험**: 학사시스템 게시판에 현장학습 일지를 쓰며 본문에 SQL 예시(`SELECT ... WHERE`)를 넣고 등록 →

```
화면:  "서버에 연결할 수 없습니다. 인터넷 연결을 확인하세요."  (네트워크 장애처럼 보임)
실제:  개발자도구(Network) 확인 → status 200 OK
       응답 본문: "The request / response that are contrary to the
                   Web firewall security policies have been blocked."
```

→ 네트워크 장애가 아니라 **WAF가 SQL 구문을 SQLi로 오탐 차단**한 것. 본문에서 SQL 문을 지우니 정상 등록됐다.

> **교훈: 에러 문구 ≠ 실제 원인.** "연결 불가"라도 status 200일 수 있다. 트러블슈팅 1순위는 [[HTTP & HTTPS]] 개발자도구로 **실제 요청/응답 확인**.

<br>

#### 3. 대응 (Troubleshooting)

----

| 관점 | 방법 |
|---|---|
| **사용자 단 (임시)** | 키워드 깨뜨리기(`UPDATE`→서술형으로 풀어쓰기), SQL 구문을 일반 문장으로 변경 |
| **운영 단 (근본)** | **WAF 룰셋 화이트리스트** — 특정 페이지/파라미터(코드리뷰 게시판 등)는 SQL 패턴 검사 제외 |
| **설계 단** | 입력은 통과시키되 서버에서 [[클린코드(Clean Code) & 시큐어코딩(Secure Coding)|PreparedStatement]]로 안전 처리 (WAF는 1차 방어, 코드 레벨 방어가 본질) |

> WAF는 **심층 방어(Defense in Depth)의 한 겹**일 뿐이다. WAF만 믿지 말고 코드 레벨([[SQL Injection]]의 PreparedStatement·입력 검증)이 함께 가야 한다.

<br>

#### 4. 면접 연결 포인트

----

"웹 보안 공격 종류와 WAF의 방어 원리, 그리고 WAF 운영 시 오탐 이슈를 설명해보세요" → [[SQL Injection]](공격/방어) + WAF(패턴 탐지) + 오탐(정상 텍스트 차단) + 화이트리스트를 묶어서 답할 수 있다.

## 관련 개념
- [[SQL Injection]]
- [[HTTP & HTTPS]]
- [[클린코드(Clean Code) & 시큐어코딩(Secure Coding)]]

<!-- 🔒 MANUAL:START — 빌드해도 안 지워짐. 30초 요약 등 직접 작성 -->
## 🎤 면접 30초 요약
> 본문을 30초 분량으로 압축. 막히면 [[🤖 Claude 학습 루프]]의 '채우기' 프롬프트 사용.

WAF는 애플리케이션 계층(L7)에서 HTTP 본문·파라미터를 검사해 SQL Injection·XSS 같은 공격 패턴을 차단하는 보안 장비입니다. 시그니처·정규식으로 `SELECT`, `' OR '1'='1'` 같은 패턴을 탐지하는데, "의도"가 아니라 "패턴"을 보기 때문에 정상 텍스트(개발 일지·보고서)도 차단되는 **오탐(False Positive)** 이 생깁니다. 실제로 게시판에 SQL 예시를 적었다가 차단됐는데, 화면엔 "서버 연결 불가"로 떴지만 status는 200이고 응답 본문에 WAF 차단 메시지가 있었습니다. 근본 해결은 WAF 룰셋 화이트리스트 예외 처리이고, WAF는 심층 방어의 한 겹일 뿐 코드 레벨의 PreparedStatement 방어가 본질입니다.
<!-- 🔒 MANUAL:END -->
