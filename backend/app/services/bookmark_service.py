import uuid
from typing import List, Dict, Any
from datetime import datetime
from app.core.database import get_supabase_client, local_db
from app.services.matcher_service import matcher_service

class BookmarkService:
    def get_bookmarks(self, user_id: str = "demo_user") -> List[Dict[str, Any]]:
        supabase = get_supabase_client()
        bookmarks_data = []

        if supabase:
            try:
                res = supabase.table("bookmarks").select("*, contests(*)").eq("user_id", user_id).execute()
                bookmarks_data = res.data or []
            except Exception as e:
                print(f"[BookmarkService] Supabase get bookmarks error: {e}")

        if not bookmarks_data:
            # Fallback to local_db
            user_bms = [b for b in local_db.bookmarks if b["user_id"] == user_id]
            for bm in user_bms:
                cid = bm["contest_id"]
                cdata = local_db.contests.get(cid)
                if not cdata:
                    for c in local_db.contests.values():
                        if str(c.get("id")) == cid:
                            cdata = c
                            break

                enriched_c = None
                if cdata:
                    enriched_c = dict(cdata)
                    enriched_c["dday"] = matcher_service.calculate_dday(cdata.get("end_date"))
                    enriched_c["is_bookmarked"] = True

                bookmarks_data.append({
                    "id": bm["id"],
                    "user_id": user_id,
                    "contest_id": cid,
                    "created_at": bm["created_at"],
                    "contest": enriched_c
                })

        return bookmarks_data

    def add_bookmark(self, user_id: str, contest_id: str) -> Dict[str, Any]:
        supabase = get_supabase_client()
        now_iso = datetime.utcnow().isoformat()
        bm_id = f"bm_{uuid.uuid4().hex[:8]}"

        if supabase:
            try:
                res = supabase.table("bookmarks").insert({
                    "user_id": user_id,
                    "contest_id": contest_id
                }).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[BookmarkService] Supabase bookmark add error: {e}")

        # Local DB 처리 (중복 체크)
        for b in local_db.bookmarks:
            if b["user_id"] == user_id and b["contest_id"] == contest_id:
                return b

        new_bm = {
            "id": bm_id,
            "user_id": user_id,
            "contest_id": contest_id,
            "created_at": now_iso
        }
        local_db.bookmarks.append(new_bm)
        return new_bm

    def remove_bookmark(self, user_id: str, contest_id: str) -> bool:
        supabase = get_supabase_client()
        if supabase:
            try:
                supabase.table("bookmarks").delete().eq("user_id", user_id).eq("contest_id", contest_id).execute()
            except Exception as e:
                print(f"[BookmarkService] Supabase bookmark delete error: {e}")

        before_len = len(local_db.bookmarks)
        local_db.bookmarks = [
            b for b in local_db.bookmarks 
            if not (b["user_id"] == user_id and b["contest_id"] == contest_id)
        ]
        return len(local_db.bookmarks) < before_len

bookmark_service = BookmarkService()
