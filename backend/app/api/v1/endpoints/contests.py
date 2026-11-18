from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.core.security import get_current_user
from app.services.contest_service import contest_service
from app.schemas.contest import ContestResponse, ContestListResponse

router = APIRouter()

@router.get("", response_model=ContestListResponse)
def get_contests(
    category: Optional[str] = Query(None, description="공모전 분야"),
    source: Optional[str] = Query(None, description="수집 출처"),
    search: Optional[str] = Query(None, description="검색 키워드"),
    sort_by: str = Query("deadline", description="정렬 (deadline: 마감임박순, latest: 최신순, interest: 관심도순)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """공모전 목록 조회 (필터링, 검색, 맞춤 랭킹 및 D-day 계산)"""
    user_id = current_user.get("id", "demo_user")
    all_contests = contest_service.get_contests(
        category=category,
        source=source,
        search=search,
        user_id=user_id,
        sort_by=sort_by
    )

    total = len(all_contests)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = all_contests[start_idx:end_idx]

    return {
        "total": total,
        "items": items,
        "page": page,
        "page_size": page_size
    }

@router.get("/recommended", response_model=List[ContestResponse])
def get_recommended_contests(
    limit: int = Query(6, ge=1, le=30),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """사용자의 관심사(분야, 키워드, 참가대상)에 기반한 맞춤 공모전 추천"""
    user_id = current_user.get("id", "demo_user")
    return contest_service.get_recommended_contests(user_id=user_id, limit=limit)

@router.get("/{id}", response_model=ContestResponse)
def get_contest_detail(
    id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """공모전 상세 정보 조회"""
    user_id = current_user.get("id", "demo_user")
    contest = contest_service.get_contest_by_id(contest_id=id, user_id=user_id)
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 공모전을 찾을 수 없습니다."
        )
    return contest
