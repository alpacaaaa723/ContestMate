from typing import Optional, Dict, Any
from datetime import date
from pydantic import BaseModel, Field

class CalendarExtendedProps(BaseModel):
    organizer: str
    category: str
    target_type: str
    dday: int
    isBookmarked: bool
    source: str
    sourceUrl: str
    prize: Optional[str] = None
    description: Optional[str] = None
    urgencyLevel: str = Field(description="normal | caution | urgent | dday | expired")

class FullCalendarEvent(BaseModel):
    id: str
    title: str
    start: str  # YYYY-MM-DD
    allDay: bool = True
    backgroundColor: str = "#3B82F6"
    borderColor: str = "#2563EB"
    textColor: str = "#FFFFFF"
    className: str = "fc-event-normal"
    extendedProps: CalendarExtendedProps
