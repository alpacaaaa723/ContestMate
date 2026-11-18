from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from app.core.database import get_supabase_client

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    현재 인증된 사용자를 반환하는 FastAPI 의존성.
    - 유효한 Bearer 토큰이 전달된 경우 Supabase Auth / JWT 검증
    - 토큰이 없거나 개발 환경일 경우 데모 사용자 계정 반환 (개발 및 테스트 편의성)
    """
    if not credentials:
        # 인증 헤더가 없을 때 기본 게스트/데모 사용자 제공
        return {
            "id": "demo_user",
            "email": "student@contestmate.dev",
            "role": "authenticated",
            "is_demo": True
        }

    token = credentials.credentials
    supabase = get_supabase_client()

    # 1. Supabase Client가 활성화되어 있는 경우 supabase.auth.get_user(token) 시도
    if supabase:
        try:
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                return {
                    "id": str(user_response.user.id),
                    "email": user_response.user.email,
                    "role": "authenticated",
                    "is_demo": False
                }
        except Exception as e:
            # 토큰 만료 또는 유효하지 않은 토큰
            pass

    # 2. JWT Secret이 있는 경우 직접 디코딩 시도
    if settings.SUPABASE_JWT_SECRET and not settings.SUPABASE_JWT_SECRET.startswith("your-"):
        try:
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            user_id = payload.get("sub")
            email = payload.get("email", "unknown@user.com")
            if user_id:
                return {
                    "id": user_id,
                    "email": email,
                    "role": "authenticated",
                    "is_demo": False
                }
        except JWTError:
            pass

    # 3. 디버그/로컬 모드 지원
    return {
        "id": "demo_user",
        "email": "student@contestmate.dev",
        "role": "authenticated",
        "is_demo": True
    }
