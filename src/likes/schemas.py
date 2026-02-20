from pydantic import BaseModel, ConfigDict 
from datetime import datetime

class LikeCreate(BaseModel):
    post_id: int
    user_id: int

class LikeOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
