from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PreferenceBase(BaseModel):
    categories: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    keyword_match_type: str = Field(default="OR", pattern="^(OR|AND)$")
    target_types: List[str] = Field(default_factory=list)
    hide_expired: bool = False
    notify_new_contests: bool = True
    notify_deadlines: bool = True
    telegram_chat_id: Optional[str] = None

class PreferenceUpdate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: str
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
