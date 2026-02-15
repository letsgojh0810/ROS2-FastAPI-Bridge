from datetime import datetime

from pydantic import BaseModel


class PositionIn(BaseModel):
    robot_id: str
    x: float
    y: float
    status: str = "active"


class PositionOut(PositionIn):
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}
