from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.services.contest_service import contest_service
from app.services.matcher_service import matcher_service
from app.core.database import local_db

class CalendarService:
    @staticmethod
    def _determine_urgency_style(dday: int) -> Dict[str, str]:
        if dday < 0:
            return {
                "urgencyLevel": "expired",
                "backgroundColor": "#9CA3AF",
                "borderColor": "#6B7280",
                "textColor": "#FFFFFF",
                "className": "fc-event-expired"
            }
        elif dday == 0:
            return {
                "urgencyLevel": "dday",
                "backgroundColor": "#DC2626",
                "borderColor": "#991B1B",
                "textColor": "#FFFFFF",
                "className": "fc-event-dday animate-pulse font-bold"
            }
        elif 1 <= dday <= 2:
            return {
                "urgencyLevel": "urgent",
                "backgroundColor": "#EF4444",
                "borderColor": "#B91C1C",
                "textColor": "#FFFFFF",
                "className": "fc-event-urgent font-semibold"
            }
        elif 3 <= dday <= 6:
            return {
                "urgencyLevel": "caution",
                "backgroundColor": "#F59E0B",
                "borderColor": "#D97706",
                "textColor": "#FFFFFF",
                "className": "fc-event-caution"
            }
        else:
            return {
                "urgencyLevel": "normal",
                "backgroundColor": "#3B82F6",
                "borderColor": "#2563EB",
                "textColor": "#FFFFFF",
                "className": "fc-event-normal"
            }

    def get_calendar_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        bookmark_only: bool = False,
        category: Optional[str] = None,
        deadline_within: Optional[int] = None,
        user_id: str = "demo_user"
    ) -> List[Dict[str, Any]]:
        contests = contest_service.get_contests(
            category=category,
            user_id=user_id,
            sort_by="deadline"
        )

        events: List[Dict[str, Any]] = []

        for c in contests:
            dday = c["dday"]
            is_bm = c["is_bookmarked"]

            # 1. 북마크 필터
            if bookmark_only and not is_bm:
                continue

            # 2. 마감 임박 필터
            if deadline_within is not None and not (0 <= dday <= deadline_within):
                continue

            # 3. 날짜 범위 필터
            c_end_str = str(c.get("end_date")).split("T")[0]
            if start_date and c_end_str < start_date:
                continue
            if end_date and c_end_str > end_date:
                continue

            style = self._determine_urgency_style(dday)
            
            dday_label = "오늘마감" if dday == 0 else (f"D+{abs(dday)}" if dday < 0 else f"D-{dday}")
            event_title = f"[{dday_label}] {c.get('title')}"

            events.append({
                "id": str(c.get("id")),
                "title": event_title,
                "start": c_end_str,
                "allDay": True,
                "backgroundColor": style["backgroundColor"],
                "borderColor": style["borderColor"],
                "textColor": style["textColor"],
                "className": style["className"],
                "extendedProps": {
                    "organizer": c.get("organizer", ""),
                    "category": c.get("category", ""),
                    "target_type": c.get("target_type", "제한없음"),
                    "dday": dday,
                    "isBookmarked": is_bm,
                    "source": c.get("source", ""),
                    "sourceUrl": c.get("source_url", ""),
                    "prize": c.get("prize", ""),
                    "description": c.get("description", ""),
                    "urgencyLevel": style["urgencyLevel"]
                }
            })

        return events

calendar_service = CalendarService()
