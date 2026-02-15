# ROS2-FastAPI-Bridge

ROS2 Gazebo 시뮬레이션 로봇의 위치를 실시간으로 웹 대시보드에서 모니터링하는 시스템.
ROS2 브릿지 노드가 로봇의 odometry 데이터를 수집하여 FastAPI 서버로 전송하고, WebSocket을 통해 브라우저에 실시간 반영한다.

## 아키텍처

```
┌─────────────────────┐
│  Gazebo Simulation  │
│  (TurtleBot3 등)    │
└────────┬────────────┘
         │ /odom 토픽 (nav_msgs/Odometry)
         ▼
┌─────────────────────┐       HTTP POST        ┌─────────────────────┐
│  ROS2 Bridge Node   │ ────────────────────▶  │   FastAPI Server    │
│                     │  /api/robot/position   │                     │
│ • /odom 구독        │                        │ • REST API          │
│ • x,y 추출         │                        │ • WebSocket 브로드캐스트│
│ • 0.5초 간격 전송   │                        │ • DB 저장            │
└─────────────────────┘                        └──────┬──────┬───────┘
                                                      │      │
                                             WebSocket │      │ SQLAlchemy
                                                      ▼      ▼
                                               ┌──────────┐ ┌──────────┐
                                               │ Browser  │ │PostgreSQL│
                                               │Dashboard │ │   DB     │
                                               │          │ │          │
                                               │• Leaflet │ │• 경로    │
                                               │  격자 맵  │ │  히스토리│
                                               │• 실시간   │ │          │
                                               │  마커 이동│ │          │
                                               └──────────┘ └──────────┘
```

## 기술 스택

| 영역 | 기술 | 설명 |
|------|------|------|
| 시뮬레이션 | ROS2 Humble + Gazebo | 로봇 시뮬레이션 환경 |
| 브릿지 | rclpy + requests | ROS2 토픽 → HTTP 변환 |
| 웹 서버 | FastAPI + SQLAlchemy (async) | 비동기 REST API + ORM |
| 실시간 통신 | WebSocket | 서버 → 브라우저 푸시 |
| DB | PostgreSQL 16 (Docker) | 경로 히스토리 저장 |
| 프론트엔드 | Leaflet.js | 격자 기반 2D 맵 시각화 |

## 프로젝트 구조

```
ROS2-FastAPI-Bridge/
├── server/                         # 웹 서버
│   ├── app/
│   │   ├── main.py                 # FastAPI 앱 진입점 (CORS, 라우터, lifespan)
│   │   ├── config.py               # 환경변수 설정 (pydantic-settings)
│   │   ├── database.py             # SQLAlchemy async 엔진/세션
│   │   ├── models.py               # DB 모델 (robot_positions 테이블)
│   │   ├── schemas.py              # Pydantic 요청/응답 스키마
│   │   ├── routers/
│   │   │   ├── robot.py            # POST /position, GET /history
│   │   │   └── websocket.py        # WebSocket 연결 관리 + 브로드캐스트
│   │   └── templates/
│   │       └── dashboard.html      # Leaflet.js 실시간 대시보드
│   ├── requirements.txt
│   └── .env.example
│
├── ros2_bridge/                    # ROS2 브릿지 노드
│   ├── robot_bridge/
│   │   ├── bridge_node.py          # /odom 구독 → HTTP POST 전송
│   │   └── config.py               # 서버 URL, 전송 주기 설정
│   ├── launch/
│   │   └── bridge_launch.py        # ros2 launch 파일
│   ├── package.xml
│   ├── setup.py
│   └── setup.cfg
│
├── docker-compose.yml              # PostgreSQL 컨테이너
└── README.md
```

## 완료된 기능 (v0.1 - Skeleton)

- [x] FastAPI 서버 구조 (비동기, CORS, 라우터 분리)
- [x] `POST /api/robot/position` - 로봇 위치 데이터 수신 및 DB 저장
- [x] `GET /api/robot/position/{robot_id}/history` - 경로 히스토리 조회
- [x] `WS /ws/robot/{robot_id}` - robot_id별 WebSocket 실시간 푸시
- [x] Leaflet.js 격자 맵 대시보드 (마커 이동, 경로 트레일, 로그 패널)
- [x] PostgreSQL Docker 구성
- [x] ROS2 브릿지 노드 틀 (`/odom` → HTTP POST, 0.5초 제한)
- [x] ROS2 패키지 구조 (package.xml, setup.py, launch)

## 구현 예정 기능

- [ ] Gazebo 시뮬레이션 환경 연동 (TurtleBot3)
- [ ] 브릿지 노드 에러 핸들링 (서버 다운 시 재시도 로직)
- [ ] orientation(theta) 데이터 추가 전송
- [ ] 다중 로봇 지원 (robot_id별 마커 색상 구분)
- [ ] 경로 재생 기능 (히스토리 데이터 애니메이션)
- [ ] 로봇 상태 확장 (배터리, 속도, 목표지점)
- [ ] 대시보드 → ROS2 명령 전송 (목표지점 클릭 → nav2 goal)
- [ ] Gazebo 맵 이미지 오버레이

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/robot/position` | 로봇 위치 수신 (ROS2 브릿지 → 서버) |
| GET | `/api/robot/position/{robot_id}/history?limit=100` | 경로 히스토리 조회 |
| WS | `/ws/robot/{robot_id}` | 실시간 위치 스트림 (서버 → 브라우저) |
| GET | `/dashboard` | 모니터링 대시보드 페이지 |
| GET | `/docs` | Swagger API 문서 (자동 생성) |

### 요청/응답 예시

```bash
# 위치 데이터 전송
curl -X POST http://localhost:8000/api/robot/position \
  -H "Content-Type: application/json" \
  -d '{"robot_id": "robot_1", "x": 1.5, "y": 2.3, "status": "active"}'

# 응답
{
  "robot_id": "robot_1",
  "x": 1.5,
  "y": 2.3,
  "status": "active",
  "id": 1,
  "timestamp": "2026-02-15T12:59:50.455607Z"
}
```

## 실행 방법

### 1. PostgreSQL 실행

```bash
docker-compose up -d
```

### 2. 웹 서버 실행

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- 서버: http://localhost:8000
- 대시보드: http://localhost:8000/dashboard
- API 문서: http://localhost:8000/docs

### 3. 서버 단독 테스트 (curl)

```bash
# 위치 데이터 연속 전송 (로봇 이동 시뮬레이션)
for i in $(seq 1 10); do
  curl -s -X POST http://localhost:8000/api/robot/position \
    -H "Content-Type: application/json" \
    -d "{\"robot_id\": \"robot_1\", \"x\": $(echo "$i * 0.5" | bc), \"y\": $(echo "$i * 0.3" | bc)}"
  sleep 0.5
done

# 히스토리 조회
curl http://localhost:8000/api/robot/position/robot_1/history
```

### 4. ROS2 브릿지 실행 (ROS2 환경 필요)

```bash
cd ros2_bridge
colcon build --packages-select robot_bridge
source install/setup.bash
ros2 launch robot_bridge bridge_launch.py
```

## DB 스키마

```sql
CREATE TABLE robot_positions (
    id          SERIAL PRIMARY KEY,
    robot_id    VARCHAR(50) NOT NULL,
    x           FLOAT NOT NULL,
    y           FLOAT NOT NULL,
    status      VARCHAR(20) DEFAULT 'active',
    timestamp   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_robot_positions_robot_id ON robot_positions (robot_id);
```
