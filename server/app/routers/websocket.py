import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """로봇 ID별 WebSocket 연결 관리"""

    def __init__(self):
        # {robot_id: [websocket, ...]}
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, robot_id: str, websocket: WebSocket):
        await websocket.accept()
        if robot_id not in self.connections:
            self.connections[robot_id] = []
        self.connections[robot_id].append(websocket)

    def disconnect(self, robot_id: str, websocket: WebSocket):
        if robot_id in self.connections:
            self.connections[robot_id].remove(websocket)
            if not self.connections[robot_id]:
                del self.connections[robot_id]

    async def broadcast(self, robot_id: str, data: dict):
        """특정 로봇의 모든 구독자에게 데이터 전송"""
        if robot_id not in self.connections:
            return
        message = json.dumps(data)
        for ws in self.connections[robot_id]:
            await ws.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/robot/{robot_id}")
async def robot_websocket(websocket: WebSocket, robot_id: str):
    await manager.connect(robot_id, websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 대기 (keepalive)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(robot_id, websocket)
