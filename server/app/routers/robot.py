from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import RobotPosition
from app.routers.websocket import manager
from app.schemas import PositionIn, PositionOut

router = APIRouter()


@router.post("/position", response_model=PositionOut)
async def create_position(data: PositionIn, db: AsyncSession = Depends(get_db)):
    """ROS2 브릿지에서 로봇 위치 수신 -> DB 저장 -> WebSocket 브로드캐스트"""
    position = RobotPosition(**data.model_dump())
    db.add(position)
    await db.commit()
    await db.refresh(position)

    # WebSocket으로 실시간 전송
    await manager.broadcast(
        data.robot_id,
        {
            "robot_id": data.robot_id,
            "x": data.x,
            "y": data.y,
            "status": data.status,
            "timestamp": position.timestamp.isoformat(),
        },
    )

    return position


@router.get("/position/{robot_id}/history", response_model=list[PositionOut])
async def get_history(
    robot_id: str, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """특정 로봇의 경로 히스토리 조회"""
    result = await db.execute(
        select(RobotPosition)
        .where(RobotPosition.robot_id == robot_id)
        .order_by(RobotPosition.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()
