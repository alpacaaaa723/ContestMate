import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import httpx
from app.core.config import settings
from app.core.database import get_supabase_client, local_db
from app.services.matcher_service import matcher_service

class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, chat_id: str, text: str) -> Dict[str, Any]:
        """텔레그램 메시지 발송 기본 메서드"""
        if not self.bot_token or not chat_id:
            return {
                "success": False,
                "error": "TELEGRAM_BOT_TOKEN 또는 telegram_chat_id가 설정되지 않았습니다."
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False
                    }
                )
                if res.status_code == 200:
                    return {"success": True, "data": res.json()}
                else:
                    return {"success": False, "error": f"Telegram API error {res.status_code}: {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _log_notification(self, user_id: str, contest_id: Optional[str], notif_type: str, status: str, error_msg: Optional[str] = None):
        supabase = get_supabase_client()
        log_entry = {
            "id": f"notif_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "contest_id": contest_id,
            "notification_type": notif_type,
            "sent_at": datetime.utcnow().isoformat(),
            "status": status,
            "error_message": error_msg
        }

        if supabase:
            try:
                supabase.table("notification_logs").insert(log_entry).execute()
            except Exception as e:
                print(f"[TelegramService] Notification log insert error: {e}")
        else:
            local_db.notification_logs.append(log_entry)

    def is_already_sent(self, user_id: str, contest_id: str, notif_type: str) -> bool:
        """중복 발송 여부 확인 (당일 이미 동일 유형으로 발송되었는지)"""
        today_str = date.today().isoformat()
        for log in local_db.notification_logs:
            if (log.get("user_id") == user_id 
                and log.get("contest_id") == contest_id 
                and log.get("notification_type") == notif_type
                and log.get("status") == "SUCCESS"
                and log.get("sent_at", "").startswith(today_str)):
                return True
        return False

    async def send_deadline_alert(self, user_id: str, contest: Dict[str, Any], dday: int) -> bool:
        user_pref = local_db.user_preferences.get(user_id, {})
        chat_id = user_pref.get("telegram_chat_id")
        if not chat_id or not user_pref.get("notify_deadlines", True):
            return False

        cid = str(contest.get("id"))
        notif_type = f"DEADLINE_D{dday}" if dday > 0 else "DEADLINE_TODAY"

        if self.is_already_sent(user_id, cid, notif_type):
            return False

        dday_text = "오늘 마감" if dday == 0 else f"마감 {dday}일 전"
        icon = "🚨" if dday == 0 else ("⚠️" if dday <= 3 else "⏰")
        
        message = (
            f"{icon} <b>[ContestMate 마감 알림] {dday_text}</b>\n\n"
            f"📌 <b>{contest.get('title')}</b>\n"
            f"🏢 주최: {contest.get('organizer')}\n"
            f"🏷 분야: {contest.get('category')}\n"
            f"🏆 상금/혜택: {contest.get('prize') or '상세 참조'}\n"
            f"📅 마감일: {contest.get('end_date')}\n\n"
            f"🔗 <a href='{contest.get('source_url')}'>공모전 공고 바로가기</a>"
        )

        res = await self.send_message(chat_id, message)
        status = "SUCCESS" if res.get("success") else "FAILED"
        self._log_notification(user_id, cid, notif_type, status, res.get("error"))
        return res.get("success", False)

    async def send_new_contest_alert(self, user_id: str, contest: Dict[str, Any]) -> bool:
        user_pref = local_db.user_preferences.get(user_id, {})
        chat_id = user_pref.get("telegram_chat_id")
        if not chat_id or not user_pref.get("notify_new_contests", True):
            return False

        cid = str(contest.get("id"))
        notif_type = "NEW_CONTEST"

        if self.is_already_sent(user_id, cid, notif_type):
            return False

        message = (
            f"✨ <b>[ContestMate 맞춤 신규 공모전]</b>\n\n"
            f"📌 <b>{contest.get('title')}</b>\n"
            f"🏢 주최: {contest.get('organizer')}\n"
            f"🏷 분야: {contest.get('category')}\n"
            f"👥 참가대상: {contest.get('target_type')}\n"
            f"📅 마감일: {contest.get('end_date')}\n\n"
            f"🔗 <a href='{contest.get('source_url')}'>공모전 상세 확인하기</a>"
        )

        res = await self.send_message(chat_id, message)
        status = "SUCCESS" if res.get("success") else "FAILED"
        self._log_notification(user_id, cid, notif_type, status, res.get("error"))
        return res.get("success", False)

    def get_notification_history(self, user_id: str = "demo_user") -> List[Dict[str, Any]]:
        history = [log for log in local_db.notification_logs if log.get("user_id") == user_id]
        enriched = []
        for h in reversed(history):
            item = dict(h)
            cid = h.get("contest_id")
            if cid and cid in local_db.contests:
                item["contest_title"] = local_db.contests[cid].get("title")
            else:
                item["contest_title"] = "공모전 알림"
            enriched.append(item)
        return enriched

telegram_service = TelegramService()
