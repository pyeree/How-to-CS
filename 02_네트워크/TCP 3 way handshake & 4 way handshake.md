---
tags: [네트워크]
status: 완료
priority: 1
복습일: 2026-08-14
aliases: ["3 way handshake", "3-way handshake", "핸드셰이크"]
출처: gyoogle
---
## [TCP] 3 way handshake & 4 way handshake

> 연결을 성립하고 해제하는 과정을 말한다

<br>

### 3 way handshake - 연결 성립

TCP는 정확한 전송을 보장해야 한다. 따라서 통신하기에 앞서, 논리적인 접속을 성립하기 위해 3 way handshake 과정을 진행한다.

<img src="https://media.geeksforgeeks.org/wp-content/uploads/TCP-connection-1.png">

1) 클라이언트가 서버에게 SYN 패킷을 보냄 (sequence : x)

2) 서버가 SYN(x)을 받고, 클라이언트로 받았다는 신호인 ACK와 SYN 패킷을 보냄 (sequence : y, ACK : x + 1)

3) 클라이언트는 서버의 응답은 ACK(x+1)와 SYN(y) 패킷을 받고, ACK(y+1)를 서버로 보냄

<br>

이렇게 3번의 통신이 완료되면 연결이 성립된다. (3번이라 3 way handshake인 것)

<br>

<br>

### 4 way handshake - 연결 해제

연결 성립 후, 모든 통신이 끝났다면 해제해야 한다.

<img src="https://media.geeksforgeeks.org/wp-content/uploads/CN.png">

1) 클라이언트는 서버에게 연결을 종료한다는 FIN 플래그를 보낸다.

2) 서버는 FIN을 받고, 확인했다는 ACK를 클라이언트에게 보낸다. (이때 모든 데이터를 보내기 위해 CLOSE_WAIT 상태가 된다)

3) 데이터를 모두 보냈다면, 연결이 종료되었다는 FIN 플래그를 클라이언트에게 보낸다.

4) 클라이언트는 FIN을 받고, 확인했다는 ACK를 서버에게 보낸다. (아직 서버로부터 받지 못한 데이터가 있을 수 있으므로 TIME_WAIT을 통해 기다린다.)

- 서버는 ACK를 받은 이후 소켓을 닫는다 (Closed)

- TIME_WAIT 시간이 끝나면 클라이언트도 닫는다 (Closed)

<br>

이렇게 4번의 통신이 완료되면 연결이 해제된다.

<br>

<br>

##### [참고 자료]

[링크](<https://www.geeksforgeeks.org/tcp-connection-termination/>)

<!-- 🔒 MANUAL:START — 빌드해도 안 지워짐. 30초 요약 등 직접 작성 -->
## 🎤 면접 30초 요약
> 본문을 30초 분량으로 압축. 막히면 [[🤖 Claude 학습 루프]]의 '채우기' 프롬프트 사용.

TCP는 정확한 전송을 보장해야 하니까, 통신 전에 논리적인 연결을 맺는 과정이 3way handshake입니다. 클라이언트가 서버한테 연결하고 싶다는 SYN을 보내면, 서버는 받았다는 ACK랑 자기도 연결하고 싶다는 SYN을 같이 보내고, 클라이언트가 마지막으로 ACK를 보내면서 3번 만에 연결이 성립됩니다.

연결을 끊을 때는 4way handshake인데, 3way보다 한 단계가 더 필요한 이유는 **서버가 곧바로 못 닫기 때문**입니다. 클라이언트가 FIN을 보내면 서버는 일단 ACK만 먼저 보내고(아직 보낼 데이터가 남아있을 수 있어서 CLOSE_WAIT 상태로 대기), 데이터를 다 보낸 다음에서야 자기도 FIN을 보냅니다. 서버 쪽에서 ACK랑 FIN이 시간차를 두고 따로 나가니까 3way처럼 합쳐서 보낼 수 없고, 왕복이 한 번 더 생기는 겁니다.

마지막으로 클라이언트는 서버의 FIN을 받고 ACK를 보낸 다음에도 바로 소켓을 안 닫고 **TIME_WAIT** 동안 기다리는데, 아직 서버로부터 못 받은 데이터가 있을 수 있기 때문입니다.

### 🔎 더 알아두면 좋은 것 (본문엔 없는 심화 — 요약 채점 대상 아님)
- **TIME_WAIT이 진짜로 필요한 이유는 두 가지다.** ① 마지막 ACK가 유실되면 서버가 FIN을 재전송하는데, 클라이언트가 이미 닫혀 있으면 그 재전송을 못 받아준다. ② 이 연결에서 떠돌던 지연 패킷이 나중에 같은 포트로 맺어진 새 연결에 섞여 들어오는 걸 막아야 한다.
- 꼬리질문으로 자주 나온다: "TIME_WAIT이 너무 많으면 어떤 문제가 생기나요?" → 소켓이 그동안 재사용이 안 돼서, 짧은 연결이 아주 많은 서버(예: 로드밸런서)에서는 포트 고갈로 이어질 수 있다.

<!-- 🔒 MANUAL:END -->
