from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.database import local_db, get_supabase_client
from app.collectors.runner import collector_runner

router = APIRouter()

@router.get("/collector-status")
def get_collector_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """사이트별 데이터 수집 상태 및 최근 로그 조회"""
    supabase = get_supabase_client()
    logs = []

    if supabase:
        try:
            res = supabase.table("collector_logs").select("*").order("started_at", desc=True).limit(20).execute()
            logs = res.data or []
        except Exception as e:
            print(f"[Admin API] Supabase logs fetch error: {e}")

    if not logs:
        logs = list(reversed(local_db.collector_logs[-20:]))

    return {
        "total_contests": len(local_db.contests),
        "recent_logs": logs,
        "collectors": [
            {
                "name": col.source_name,
                "base_url": col.base_url,
                "status": "ACTIVE"
            }
            for col in collector_runner.collectors
        ]
    }

@router.post("/collect-now")
async def trigger_collect_now(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """공모전 데이터 즉시 수집 실행 (온디맨드)"""
    summary = await collector_runner.run_all()
    return {
        "message": "공모전 데이터 수집 작업이 완료되었습니다.",
        "summary": summary,
        "total_contests_now": len(local_db.contests)
    }
