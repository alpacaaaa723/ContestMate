import asyncio
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.collectors.runner import collector_runner
from app.services.telegram_service import telegram_service
from app.services.contest_service import contest_service
from app.core.database import local_db
from app.core.config import settings

scheduler = AsyncIOScheduler()

async def scheduled_scraping_job():
    """주기적 공모전 수집 작업"""
    print("[APScheduler] Starting scheduled scraping job...")
    try:
        results = await collector_runner.run_all()
        print(f"[APScheduler] Scraping job completed: {results}")
    except Exception as e:
        print(f"[APScheduler] Scraping job failed: {e}")

async def scheduled_deadline_alert_job():
    """일일 마감 임박 알림 발송 작업 (D-7, D-3, D-1, 당일)"""
    print("[APScheduler] Checking deadline alerts...")
    try:
        for user_id, pref in local_db.user_preferences.items():
            if not pref.get("telegram_chat_id") or not pref.get("notify_deadlines", True):
                continue

            contests = contest_service.get_contests(user_id=user_id)
            target_ddays = {0, 1, 3, 7}

            for c in contests:
                dday = c.get("dday")
                if dday in target_ddays:
                    # 북마크되었거나 매칭 점수가 높은 공모전에 대해 알림
                    if c.get("is_bookmarked") or c.get("match_score", 0) >= 20:
                        await telegram_service.send_deadline_alert(user_id, c, dday)
    except Exception as e:
        print(f"[APScheduler] Deadline alert job error: {e}")

def start_scheduler():
    """FastAPI 시작 시 스케줄러 등록 및 가동"""
    interval_hours = settings.SCRAPER_INTERVAL_HOURS
    scheduler.add_job(
        scheduled_scraping_job,
        "interval",
        hours=interval_hours,
        id="contest_scraping_job",
        replace_existing=True
    )

    # 매일 오전 9시 마감 알림 체크 (테스트 편의를 위해 주기 실행도 가능)
    scheduler.add_job(
        scheduled_deadline_alert_job,
        "cron",
        hour=9,
        minute=0,
        id="deadline_alert_job",
        replace_existing=True
    )

    if not scheduler.running:
        scheduler.start()
        print("[APScheduler] Background scheduler started successfully.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[APScheduler] Background scheduler stopped.")
