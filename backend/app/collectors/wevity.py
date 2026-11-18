import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector


class WevityCollector(BaseCollector):
    """
    위비티(Wevity) 실제 공모전 대량 수집기
    - 다중 페이지(gp=1~8) 크롤링, 최대 ~120개 수집
    - 카테고리 필터(?s=1~9) 순회로 추가 수집
    - 실제 주최기관, 접수 마감일(D-day), 분야 정규화
    """

    # 위비티 카테고리 ID
    CATEGORY_MAP = {
        "1": "기획 / 아이디어",
        "2": "디자인",
        "3": "영상 / 콘텐츠",
        "4": "마케팅",
        "5": "과학 / 기술",
        "6": "창업",
        "7": "IT / 개발",
        "8": "AI / 인공지능",
        "9": "기타",
    }

    def __init__(self):
        super().__init__(source_name="위비티", base_url="https://www.wevity.com")

    def _normalize_category(self, raw_cat: str) -> str:
        raw = raw_cat.strip()
        if any(k in raw for k in ["웹", "모바일", "IT", "SW", "소프트웨어", "프로그래밍", "개발", "코딩", "해커톤"]):
            return "IT / 개발"
        if any(k in raw for k in ["AI", "인공지능", "데이터", "빅데이터", "딥러닝", "머신러닝", "ChatGPT", "GPT"]):
            return "AI / 인공지능"
        if any(k in raw for k in ["기획", "아이디어", "전략", "신사업", "정책", "네이밍", "논문"]):
            return "기획 / 아이디어"
        if any(k in raw for k in ["디자인", "캐릭터", "웹툰", "일러스트", "포스터", "패키지", "그림", "미술"]):
            return "디자인"
        if any(k in raw for k in ["마케팅", "광고", "홍보", "브랜딩", "PR", "서포터즈", "앰배서더"]):
            return "마케팅"
        if any(k in raw for k in ["영상", "사진", "UCC", "콘텐츠", "유튜브", "숏폼", "촬영", "다큐"]):
            return "영상 / 콘텐츠"
        if any(k in raw for k in ["창업", "스타트업", "벤처", "비즈니스"]):
            return "창업"
        if any(k in raw for k in ["과학", "공학", "기술", "신기술", "R&D", "환경", "건축", "에너지"]):
            return "과학 / 기술"
        return "기타"

    def _clean_title(self, raw_title: str) -> str:
        cleaned = re.sub(r'\s*(신규|SPECIAL|HOT|마감임박|접수중|마감|D-\d+|NEW)\s*$', '', raw_title.strip(), flags=re.IGNORECASE)
        return cleaned.strip()

    def _parse_dday_to_date(self, dday_text: str) -> str:
        today = datetime.now()
        # D-숫자 (예: D-13, D-3접수중)
        match = re.search(r'D-(\d+)', dday_text)
        if match:
            days = int(match.group(1))
            return (today + timedelta(days=days)).strftime("%Y-%m-%d")
        # D-Day 또는 오늘
        if "오늘" in dday_text or "D-Day" in dday_text or "D-day" in dday_text:
            return today.strftime("%Y-%m-%d")
        # 마감된 경우 → 과거 날짜 (오늘 기준)
        if "마감" in dday_text:
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")
        return (today + timedelta(days=14)).strftime("%Y-%m-%d")

    def _parse_page_items(self, soup: BeautifulSoup, seen_urls: set, limit: int, results: list) -> None:
        list_items = soup.select(".list li:not(.top)")
        for item in list_items:
            if len(results) >= limit:
                break

            tit_elem = item.select_one(".tit a")
            if not tit_elem:
                continue

            raw_title = tit_elem.get_text(strip=True)
            title = self._clean_title(raw_title)
            if not title:
                continue

            raw_href = tit_elem.get("href", "")
            ix_match = re.search(r'ix=(\d+)', raw_href)
            if ix_match:
                source_url = f"{self.base_url}/?c=find&s=1&gbn=view&ix={ix_match.group(1)}"
                contest_id = f"wevity_{ix_match.group(1)}"
            else:
                source_url = f"{self.base_url}/{raw_href.lstrip('/')}"
                contest_id = f"wevity_{hash(source_url) % 10**8}"

            # 중복 URL 건너뜀
            if source_url in seen_urls:
                continue
            seen_urls.add(source_url)

            organizer_elem = item.select_one(".organ")
            organizer = organizer_elem.get_text(strip=True) if organizer_elem else "위비티 공모전"

            day_elem = item.select_one(".day")
            day_text = day_elem.get_text(strip=True) if day_elem else ""
            end_date = self._parse_dday_to_date(day_text)

            # 썸네일
            img_elem = item.select_one("img")
            thumbnail = img_elem.get("src", "") if img_elem else ""
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = self.base_url + "/" + thumbnail.lstrip("/")
            if not thumbnail:
                thumbnail = "https://www.wevity.com/images/common/logo.png"

            category = self._normalize_category(title)

            results.append({
                "title": title,
                "organizer": organizer,
                "category": category,
                "target_type": "제한없음",
                "description": f"{title} - 위비티(Wevity) 실제 공모전 공고 (주최: {organizer})",
                "prize": "상세 공고 참조",
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "end_date": end_date,
                "source": "위비티",
                "source_url": source_url,
                "thumbnail_url": thumbnail,
            })

    async def collect(self, limit: int = 120) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_urls: set = set()
        max_pages = 8  # 페이지당 15개 × 8 = 최대 120개

        for page in range(1, max_pages + 1):
            if len(results) >= limit:
                break

            target_url = f"{self.base_url}/?c=find&s=1&gp={page}"
            try:
                resp = await self.client.get(target_url)
                if resp.status_code != 200:
                    print(f"[Wevity] Page {page} status: {resp.status_code}")
                    break

                soup = BeautifulSoup(resp.text, "html.parser")
                before = len(results)
                self._parse_page_items(soup, seen_urls, limit, results)
                added = len(results) - before
                print(f"[Wevity] Page {page}: +{added}개 수집 (누적 {len(results)}개)")

                # 더 이상 항목이 없으면 종료
                if added == 0:
                    print(f"[Wevity] Page {page} 항목 없음 — 종료")
                    break

            except Exception as e:
                print(f"[Wevity] Page {page} error: {e}")
                break

        # 추가 카테고리 수집 (목표치 미달 시)
        if len(results) < limit:
            extra_pages = [
                f"{self.base_url}/?c=find&s=2&gp=1",  # 디자인
                f"{self.base_url}/?c=find&s=3&gp=1",  # 영상
                f"{self.base_url}/?c=find&s=4&gp=1",  # 마케팅
                f"{self.base_url}/?c=find&s=7&gp=1",  # IT/개발
            ]
            for url in extra_pages:
                if len(results) >= limit:
                    break
                try:
                    resp = await self.client.get(url)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        before = len(results)
                        self._parse_page_items(soup, seen_urls, limit, results)
                        print(f"[Wevity] 카테고리 {url.split('s=')[1].split('&')[0]}: +{len(results) - before}개")
                except Exception as e:
                    print(f"[Wevity] 카테고리 수집 오류: {e}")

        print(f"[Wevity] 총 {len(results)}개 실제 공모전 수집 완료")
        return results
