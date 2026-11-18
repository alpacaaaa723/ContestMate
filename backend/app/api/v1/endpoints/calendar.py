from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.services.calendar_service import calendar_service
from app.schemas.calendar import FullCalendarEvent

router = APIRouter()

@router.get("/events", response_model=List[FullCalendarEvent])
def get_calendar_events(
    start: Optional[str] = Query(None, description="조회 시작일 (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="조회 마감일 (YYYY-MM-DD)"),
    bookmark_only: bool = Query(False, description="북마크한 공모전만 표시"),
    category: Optional[str] = Query(None, description="분야별 필터"),
    deadline_within: Optional[int] = Query(None, description="N일 이내 마감 공모전 필터"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    FullCalendar 표준 이벤트 JSON 반환 API
    - 마감일(end_date) 기준
    - D-day 자동 계산 및 시각적 색상 클래스 적용
    - 북마크 및 맞춤 필터 지원
    """
    user_id = current_user.get("id", "demo_user")
    return calendar_service.get_calendar_events(
        start_date=start,
        end_date=end,
        bookmark_only=bookmark_only,
        category=category,
        deadline_within=deadline_within,
        user_id=user_id
    )
