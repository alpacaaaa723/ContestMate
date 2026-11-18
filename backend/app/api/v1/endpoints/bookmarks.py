from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.services.bookmark_service import bookmark_service
from app.schemas.bookmark import BookmarkResponse

router = APIRouter()

@router.get("", response_model=List[BookmarkResponse])
def get_user_bookmarks(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """현재 사용자가 저장한 북마크 목록 조회"""
    user_id = current_user.get("id", "demo_user")
    return bookmark_service.get_bookmarks(user_id=user_id)

@router.post("/{contest_id}")
def add_bookmark(
    contest_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """공모전 북마크 추가"""
    user_id = current_user.get("id", "demo_user")
    result = bookmark_service.add_bookmark(user_id=user_id, contest_id=contest_id)
    return {"message": "북마크에 성공적으로 추가되었습니다.", "bookmark": result}

@router.delete("/{contest_id}")
def remove_bookmark(
    contest_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """공모전 북마크 제거"""
    user_id = current_user.get("id", "demo_user")
    success = bookmark_service.remove_bookmark(user_id=user_id, contest_id=contest_id)
    return {"message": "북마크가 해제되었습니다.", "removed": success}
