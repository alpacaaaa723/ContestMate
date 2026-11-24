import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector


class CampuspickCollector(BaseCollector):
    """
    캠퍼스픽 (Campuspick, https://www.campuspick.com) 실제 공모전 및 대외활동 수집기
    - 공모전 카테고리별(1~10) 및 대외활동 순회
    - 실제 포스터 고해상도 썸네일, 주최사, 상세 URL 수집
    """

    CATEGORIES = [
        (6, "IT / 개발"),        # 웹/모바일/IT
        (7, "IT / 개발"),        # 게임/소프트웨어
        (8, "과학 / 기술"),      # 과학/공학
        (1, "기획 / 아이디어"),  # 기획/아이디어
        (2, "마케팅"),           # 광고/마케팅
        (4, "디자인"),           # 디자인/순수미술
        (5, "디자인"),           # 캐릭터/만화
        (10, "영상 / 콘텐츠"),   # UCC/영상
        (3, "기획 / 아이디어"),  # 논문/리포트
    ]

    def __init__(self):
        super().__init__(source_name="캠퍼스픽", base_url="https://www.campuspick.com")

    def _normalize_category(self, title: str, default_cat: str) -> str:
        if any(k in title for k in ["AI", "인공지능", "데이터", "빅데이터", "딥러닝"]):
            return "AI / 인공지능"
        if any(k in title for k in ["해커톤", "코딩", "SW", "개발", "IT", "프로그래밍", "앱", "웹"]):
            return "IT / 개발"
        if any(k in title for k in ["기획", "아이디어", "전략", "정책", "네이밍"]):
            return "기획 / 아이디어"
        if any(k in title for k in ["디자인", "포스터", "캐릭터", "일러스트", "웹툰"]):
            return "디자인"
        if any(k in title for k in ["마케팅", "광고", "PR", "홍보", "서포터즈", "기자단"]):
            return "마케팅"
        if any(k in title for k in ["영상", "숏폼", "사진", "UCC", "유튜브"]):
            return "영상 / 콘텐츠"
        if any(k in title for k in ["창업", "스타트업", "비즈니스"]):
            return "창업"
        if any(k in title for k in ["과학", "공학", "기술", "환경"]):
            return "과학 / 기술"
        return default_cat

    async def collect(self, limit: int = 100) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_ids = set()

        # 1. 공모전 카테고리별 수집
        urls = [f"{self.base_url}/contest?category={cat_id}" for cat_id, _ in self.CATEGORIES]
        # 2. 메인 공모전 및 대외활동 추가
        urls.insert(0, f"{self.base_url}/contest")
        urls.append(f"{self.base_url}/activity")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"
        }

        for idx, target_url in enumerate(urls):
            if len(results) >= limit:
                break

            default_cat = "기타"
            if "category=" in target_url:
                c_id = int(target_url.split("category=")[-1])
                for cid, cname in self.CATEGORIES:
                    if cid == c_id:
                        default_cat = cname
                        break
            elif "activity" in target_url:
                default_cat = "마케팅"

            try:
                resp = await self.client.get(target_url, headers=headers, timeout=12.0)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select("a[href*='/contest/view'], a[href*='/activity/view']")

                for item in items:
                    if len(results) >= limit:
                        break

                    href = item.get("href", "")
                    m_id = re.search(r'id=(\d+)', href)
                    if not m_id:
                        continue
                    post_id = m_id.group(1)
                    if post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)

                    title_el = item.select_one("h3, .title, strong")
                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title or len(title) < 4:
                        continue

                    organizer_el = item.select_one("p, .organizer, .company")
                    organizer = organizer_el.get_text(strip=True) if organizer_el else "캠퍼스픽 등록 주최사"

                    img_el = item.select_one("img")
                    thumbnail = img_el.get("src") if img_el else ""
                    if not thumbnail or not thumbnail.startswith("http"):
                        thumbnail = "https://www.campuspick.com/images/common/logo.png"

                    # D-day / 마감일 추출
                    dday_el = item.select_one(".dday, [class*='dday'], .badge")
                    end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                    if dday_el:
                        d_text = dday_el.get_text(strip=True)
                        m_dday = re.search(r'D-(\d+)', d_text)
                        if m_dday:
                            end_date = (datetime.now() + timedelta(days=int(m_dday.group(1)))).strftime("%Y-%m-%d")

                    category = self._normalize_category(title, default_cat)
                    source_url = f"{self.base_url}{href}" if href.startswith("/") else href

                    results.append({
                        "title": title,
                        "organizer": organizer,
                        "category": category,
                        "target_type": "대학생, 청년",
                        "description": f"{title} - 캠퍼스픽(Campuspick) 등록 공고 (주최: {organizer})",
                        "prize": "상세 페이지 참조",
                        "start_date": datetime.now().strftime("%Y-%m-%d"),
                        "end_date": end_date,
                        "source": "캠퍼스픽",
                        "source_url": source_url,
                        "thumbnail_url": thumbnail
                    })

            except Exception as e:
                print(f"[Campuspick] Error ({target_url}): {e}")

        print(f"[Campuspick] 총 {len(results)}개 실제 공모전/대외활동 수집 완료")
        return results
