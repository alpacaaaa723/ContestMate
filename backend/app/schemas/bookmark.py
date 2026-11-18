from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.contest import ContestResponse

class BookmarkCreate(BaseModel):
    contest_id: str

class BookmarkResponse(BaseModel):
    id: str
    user_id: str
    contest_id: str
    created_at: Optional[datetime] = None
    contest: Optional[ContestResponse] = None

    class Config:
        from_attributes = True
