from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

class ContestBase(BaseModel):
    title: str
    organizer: str
    category: str
    target_type: str = "제한없음"
    description: Optional[str] = None
    prize: Optional[str] = None
    start_date: Optional[date] = None
    end_date: date
    source: str
    source_url: str
    thumbnail_url: Optional[str] = None

class ContestCreate(ContestBase):
    pass

class ContestResponse(ContestBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_crawled_at: Optional[datetime] = None
    
    # 런타임 계산 속성
    dday: int = Field(description="마감일까지 남은 일수 (0: 당일, 음수: 마감)")
    is_bookmarked: bool = False
    match_score: Optional[int] = 0
    matched_reasons: List[str] = []

    class Config:
        from_attributes = True

class ContestListResponse(BaseModel):
    total: int
    items: List[ContestResponse]
    page: int
    page_size: int
