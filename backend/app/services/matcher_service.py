from typing import Dict, Any, List, Tuple
from datetime import datetime, date

class MatcherService:
    """
    사용자 선호도(관심분야, 키워드 OR/AND, 참가대상, 상금여부 등)를 바탕으로
    공모전의 적합도를 계산하고 정렬하는 서비스
    """

    @staticmethod
    def calculate_dday(end_date_val: Any) -> int:
        if isinstance(end_date_val, str):
            try:
                end_dt = datetime.strptime(end_date_val.split("T")[0], "%Y-%m-%d").date()
            except ValueError:
                return 0
        elif isinstance(end_date_val, (datetime, date)):
            end_dt = end_date_val.date() if isinstance(end_date_val, datetime) else end_date_val
        else:
            return 0

        today = date.today()
        return (end_dt - today).days

    @staticmethod
    def evaluate_contest(
        contest: Dict[str, Any], 
        preferences: Dict[str, Any], 
        bookmarked_ids: List[str]
    ) -> Tuple[int, List[str]]:
        score = 0
        reasons = []

        cid = str(contest.get("id"))
        title = contest.get("title", "")
        category = contest.get("category", "")
        target_type = contest.get("target_type", "")
        description = contest.get("description", "") or ""
        prize = contest.get("prize", "") or ""
        text_corpus = f"{title} {description} {category}".lower()

        # 1. 북마크 여부
        if cid in bookmarked_ids:
            score += 50
            reasons.append("북마크 저장됨")

        # 2. 관심 분야 일치
        user_categories = preferences.get("categories", [])
        if category in user_categories or any(c.lower() in category.lower() for c in user_categories):
            score += 30
            reasons.append(f"관심분야 '{category}' 일치")

        # 3. 키워드 매칭 (OR / AND 지원)
        user_keywords = preferences.get("keywords", [])
        match_type = preferences.get("keyword_match_type", "OR").upper()

        if user_keywords:
            matched_kw = [kw for kw in user_keywords if kw.lower() in text_corpus]
            if match_type == "AND":
                if len(matched_kw) == len(user_keywords):
                    score += 40
                    reasons.append(f"필수 키워드 모두 일치 ({', '.join(matched_kw)})")
                else:
                    score -= 20  # AND 조건 불만족 시 감점
            else:  # OR
                if matched_kw:
                    score += len(matched_kw) * 15
                    reasons.append(f"키워드 일치 ({', '.join(matched_kw)})")

        # 4. 참가 대상 일치
        user_targets = preferences.get("target_types", [])
        if user_targets:
            if "제한없음" in target_type or any(t.lower() in target_type.lower() for t in user_targets):
                score += 10
                reasons.append("참가대상 적합")

        # 5. 상금 여부
        if any(w in prize for w in ["만원", "천만원", "억", "달러", "$"]):
            score += 5
            reasons.append("상금 혜택 있음")

        return max(score, 0), reasons

    @classmethod
    def filter_and_rank_contests(
        cls,
        contests: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        bookmarked_ids: List[str],
        sort_by: str = "deadline"  # deadline | latest | interest
    ) -> List[Dict[str, Any]]:
        hide_expired = preferences.get("hide_expired", False)
        enriched = []

        for c in contests:
            dday = cls.calculate_dday(c.get("end_date"))
            if hide_expired and dday < 0:
                continue

            score, reasons = cls.evaluate_contest(c, preferences, bookmarked_ids)
            item = dict(c)
            item["dday"] = dday
            item["is_bookmarked"] = str(c.get("id")) in bookmarked_ids
            item["match_score"] = score
            item["matched_reasons"] = reasons
            enriched.append(item)

        # 정렬
        if sort_by == "deadline":
            # 마감 임박순: D-day가 0 이상인 것을 먼저 오름차순, 마감된 것은 맨 뒤
            enriched.sort(key=lambda x: (x["dday"] < 0, x["dday"]))
        elif sort_by == "latest":
            enriched.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "interest":
            enriched.sort(key=lambda x: x["match_score"], reverse=True)

        return enriched

matcher_service = MatcherService()
