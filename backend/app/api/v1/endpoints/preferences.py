from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.database import get_supabase_client, local_db
from app.schemas.preference import PreferenceResponse, PreferenceUpdate

router = APIRouter()

@router.get("", response_model=PreferenceResponse)
def get_user_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user.get("id", "demo_user")
    supabase = get_supabase_client()

    if supabase:
        try:
            res = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"[Preferences API] Supabase error: {e}")

    # Fallback local_db
    pref = local_db.user_preferences.get(user_id)
    if not pref:
        pref = {
            "id": f"pref_{user_id}",
            "user_id": user_id,
            "categories": ["IT / 개발", "AI / 인공지능"],
            "keywords": ["해커톤", "AI", "대학생", "개발"],
            "keyword_match_type": "OR",
            "target_types": ["대학생", "제한없음"],
            "hide_expired": False,
            "notify_new_contests": True,
            "notify_deadlines": True,
            "telegram_chat_id": ""
        }
        local_db.user_preferences[user_id] = pref

    return pref

@router.put("", response_model=PreferenceResponse)
def update_user_preferences(
    update_data: PreferenceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user.get("id", "demo_user")
    supabase = get_supabase_client()
    data_dict = update_data.model_dump()

    if supabase:
        try:
            res = supabase.table("user_preferences").upsert({
                "user_id": user_id,
                **data_dict
            }, on_conflict="user_id").execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"[Preferences API] Supabase update error: {e}")

    # Local DB 업데이트
    existing = local_db.user_preferences.get(user_id, {"id": f"pref_{user_id}", "user_id": user_id})
    updated = {**existing, **data_dict}
    local_db.user_preferences[user_id] = updated
    return updated
