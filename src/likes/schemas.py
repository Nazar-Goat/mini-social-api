from pydantic import BaseModel, ConfigDict 
from datetime import datetime

class LikeResponse(BaseModel):
    message: str
    action: str  # "liked" | "unliked" | "none"