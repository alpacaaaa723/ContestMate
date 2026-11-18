from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.services.telegram_service import telegram_service
from app.schemas.notification import NotificationLogResponse, NotificationTestRequest
from app.core.database import local_db

router = APIRouter()

@router.get("/history", response_model=List[NotificationLogResponse])
def get_notification_history(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """현재 사용자의 텔레그램 알림 발송 이력 조회"""
    user_id = current_user.get("id", "demo_user")
    return telegram_service.get_notification_history(user_id=user_id)

@router.post("/test")
async def test_telegram_notification(
    req: NotificationTestRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    텔레그램 봇 연동 테스트 메시지 발송 API
    - chat_id를 직접 제공하거나, 사용자의 preference에 등록된 chat_id로 테스트 메시지 발송
    """
    user_id = current_user.get("id", "demo_user")
    user_pref = local_db.user_preferences.get(user_id, {})
    chat_id = req.telegram_chat_id or user_pref.get("telegram_chat_id")

    if not chat_id:
        raise HTTPException(
            status_code=400,
            detail="telegram_chat_id가 입력되지 않았습니다. 설정 페이지에서 먼저 등록해 주세요."
        )

    test_message = req.message or (
        "🎉 <b>[ContestMate 텔레그램 연동 성공!]</b>\n\n"
        "축하합니다! 텔레그램 봇 알림 서비스가 성공적으로 연결되었습니다.\n"
        "앞으로 설정하신 관심 공모전의 신규 등록 및 마감 임박 알림을 이 챗방으로 보내드립니다."
    )

    result = await telegram_service.send_message(chat_id, test_message)
    status_str = "SUCCESS" if result.get("success") else "FAILED"
    telegram_service._log_notification(
        user_id=user_id,
        contest_id=None,
        notif_type="TEST_MESSAGE",
        status=status_str,
        error_msg=result.get("error")
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=502,
            detail=f"텔레그램 메시지 발송 실패: {result.get('error')}"
        )

    return {
        "success": True,
        "message": "테스트 알림 메시지가 성공적으로 발송되었습니다.",
        "chat_id": chat_id
    }
