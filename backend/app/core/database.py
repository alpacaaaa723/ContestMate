import os
from typing import Optional, Dict, Any, List
from app.core.config import settings

try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    Client = Any
    create_client = None
    HAS_SUPABASE_LIB = False

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """Supabase 서비스 클라이언트 반환 (유효한 URL/키가 있을 경우)"""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not HAS_SUPABASE_LIB:
        return None

    if (settings.SUPABASE_URL 
        and not settings.SUPABASE_URL.startswith("https://your-project")
        and settings.SUPABASE_SERVICE_ROLE_KEY 
        and not settings.SUPABASE_SERVICE_ROLE_KEY.startswith("your-service")):
        try:
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            return _supabase_client
        except Exception as e:
            print(f"[Supabase Client Warning] Failed to initialize real Supabase client: {e}")
            return None
    return None

class LocalDataStore:
    """
    Supabase가 설정되지 않은 로컬 개발/테스트 환경에서도
    모든 API와 수집기가 온전히 동작할 수 있도록 지원하는 인메모리 저장소
    """
    def __init__(self):
        self.contests: Dict[str, Dict[str, Any]] = {}
        self.bookmarks: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Dict[str, Any]] = {
            "demo_user": {
                "id": "pref_demo_001",
                "user_id": "demo_user",
                "categories": ["IT / 개발", "AI / 인공지능", "기획 / 아이디어"],
                "keywords": ["해커톤", "AI", "대학생", "개발"],
                "keyword_match_type": "OR",
                "target_types": ["대학생", "제한없음"],
                "hide_expired": False,
                "notify_new_contests": True,
                "notify_deadlines": True,
                "telegram_chat_id": ""
            }
        }
        self.notification_logs: List[Dict[str, Any]] = []
        self.collector_logs: List[Dict[str, Any]] = []

local_db = LocalDataStore()
