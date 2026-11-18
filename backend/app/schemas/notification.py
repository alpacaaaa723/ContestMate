from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class NotificationLogResponse(BaseModel):
    id: str
    user_id: str
    contest_id: Optional[str] = None
    notification_type: str
    sent_at: datetime
    status: str
    error_message: Optional[str] = None
    contest_title: Optional[str] = None

    class Config:
        from_attributes = True

class NotificationTestRequest(BaseModel):
    telegram_chat_id: Optional[str] = None
    message: Optional[str] = None
