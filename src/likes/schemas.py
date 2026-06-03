from pydantic import BaseModel


class LikeResponse(BaseModel):
    message: str
    action: str  # "liked" | "unliked" | "none"