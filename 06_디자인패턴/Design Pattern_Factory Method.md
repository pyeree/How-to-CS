---
tags: [디자인패턴]
status: 완료
priority: 1
복습일: 2026-07-23
aliases: ["팩토리 메서드", "팩토리 패턴"]
출처: gyoogle
---
#### Design Pattern - Factory Method Pattern

---

한 줄 설명 : 객체를 만드는 부분을 Sub class에 맡기는 패턴.

> Robot (추상 클래스)
>
> ​	ㄴ SuperRobot
>
> ​	ㄴ PowerRobot
>
> RobotFactory (추상 클래스)
>
> ​	ㄴ SuperRobotFactory
>
> ​	ㄴ ModifiedSuperRobotFactory

즉 Robot이라는 클래스를 RobotFactory에서 생성함.

- RobotFactory 클래스 생성

```java
public abstract class RobotFactory {
	abstract Robot createRobot(String name);
}
```

* SuperRobotFactory 클래스 생성

```java
public class SuperRobotFactory extends RobotFactory {
	@Override
	Robot createRobot(String name) {
		switch(name) {
		case "super" :
			return new SuperRobot();
		case "power" :
			return new PowerRobot();
		}
		return null;
	}
}
```

생성하는 클래스를 따로 만듬...

그 클래스는 factory 클래스를 상속하고 있기 때문에, 반드시 createRobot을 선언해야 함.

name으로 건너오는 값에 따라서, 생성되는 Robot이 다르게 설계됨.

---

정리하면, 생성하는 객체를 별도로 둔다. 그리고, 그 객체에 넘어오는 값에 따라서, 다른 로봇 (피자)를 만들어 낸다.

<!-- 🔒 MANUAL:START — 빌드해도 안 지워짐. 30초 요약 등 직접 작성 -->
## 🎤 면접 30초 요약
> 본문을 30초 분량으로 압축. 막히면 [[🤖 Claude 학습 루프]]의 '채우기' 프롬프트 사용.

<!-- 🔒 MANUAL:END -->
