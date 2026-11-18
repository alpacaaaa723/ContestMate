from typing import List, Dict, Any, Optional
from datetime import date
from app.core.database import get_supabase_client, local_db
from app.services.matcher_service import matcher_service
from app.collectors.runner import DEFAULT_SEED_CONTESTS, collector_runner

class ContestService:
    @staticmethod
    def _ensure_data():
        if len(local_db.contests) == 0:
            collector_runner._save_contests(DEFAULT_SEED_CONTESTS)

    def get_contests(
        self,
        category: Optional[str] = None,
        source: Optional[str] = None,
        target_type: Optional[str] = None,
        search: Optional[str] = None,
        deadline_within: Optional[int] = None,
        user_id: str = "demo_user",
        sort_by: str = "deadline"
    ) -> List[Dict[str, Any]]:
        self._ensure_data()
        supabase = get_supabase_client()
        raw_contests = []

        if supabase:
            try:
                query = supabase.table("contests").select("*")
                if category and category != "전체":
                    query = query.eq("category", category)
                if source and source != "전체":
                    query = query.eq("source", source)
                res = query.execute()
                raw_contests = res.data or []
            except Exception as e:
                print(f"[ContestService] Supabase query failed: {e}")
                raw_contests = list(local_db.contests.values())
        else:
            raw_contests = list(local_db.contests.values())

        # 사용자 설정 및 북마크 조회
        user_pref = local_db.user_preferences.get(user_id, {})
        bookmarked_ids = [
            b["contest_id"] for b in local_db.bookmarks if b["user_id"] == user_id
        ]

        # 필터링
        filtered = []
        for c in raw_contests:
            if category and category != "전체" and c.get("category") != category:
                continue
            if source and source != "전체" and c.get("source") != source:
                continue
            if search:
                s_lower = search.lower()
                title_desc = f"{c.get('title', '')} {c.get('organizer', '')} {c.get('description', '')}".lower()
                if s_lower not in title_desc:
                    continue
            filtered.append(c)

        # 랭킹 및 D-day 계산
        ranked = matcher_service.filter_and_rank_contests(
            filtered, user_pref, bookmarked_ids, sort_by=sort_by
        )

        if deadline_within is not None:
            ranked = [c for c in ranked if 0 <= c["dday"] <= deadline_within]

        return ranked

    def get_contest_by_id(self, contest_id: str, user_id: str = "demo_user") -> Optional[Dict[str, Any]]:
        self._ensure_data()
        contest = local_db.contests.get(contest_id)
        if not contest:
            for c in local_db.contests.values():
                if str(c.get("id")) == contest_id:
                    contest = c
                    break

        if not contest:
            return None

        user_pref = local_db.user_preferences.get(user_id, {})
        bookmarked_ids = [b["contest_id"] for b in local_db.bookmarks if b["user_id"] == user_id]
        score, reasons = matcher_service.evaluate_contest(contest, user_pref, bookmarked_ids)

        res = dict(contest)
        res["dday"] = matcher_service.calculate_dday(contest.get("end_date"))
        res["is_bookmarked"] = str(contest.get("id")) in bookmarked_ids
        res["match_score"] = score
        res["matched_reasons"] = reasons
        return res

    def get_recommended_contests(self, user_id: str = "demo_user", limit: int = 10) -> List[Dict[str, Any]]:
        contests = self.get_contests(user_id=user_id, sort_by="interest")
        # 추천 점수가 15점 이상인 공모전 우선 선택
        recommended = [c for c in contests if c.get("match_score", 0) >= 15]
        return recommended[:limit] if recommended else contests[:limit]

contest_service = ContestService()
