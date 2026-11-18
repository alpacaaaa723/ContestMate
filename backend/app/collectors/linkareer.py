import json
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector


class LinkareerCollector(BaseCollector):
    """
    링커리어(Linkareer) 실제 공모전 수집기
    - Next.js __NEXT_DATA__ SSR + HTML 직접 파싱 병행
    - 여러 카테고리 URL 순회 (공모전, 서포터즈, 대외활동)
    - 실제 포스터 이미지, 활동 고유 URL
    """

    # 링커리어 카테고리 URL 목록
    LIST_URLS = [
        "/list/contest",           # 공모전
        "/list/supporter",         # 서포터즈/홍보단
        "/list/activity",          # 대외활동
        "/list/contest?page=2",    # 공모전 2페이지
        "/list/contest?page=3",    # 공모전 3페이지
        "/list/intern",            # 인턴
    ]

    def __init__(self):
        super().__init__(source_name="링커리어", base_url="https://linkareer.com")

    def _normalize_category(self, title: str, tags: list = None) -> str:
        text = title + " " + " ".join(tags or [])
        if any(k in text for k in ["IT", "개발", "코딩", "SW", "해커톤", "웹", "앱", "프로그래밍"]):
            return "IT / 개발"
        if any(k in text for k in ["AI", "인공지능", "데이터", "빅데이터", "ChatGPT", "GPT"]):
            return "AI / 인공지능"
        if any(k in text for k in ["기획", "아이디어", "서포터즈", "홍보단", "앰배서더", "기자단"]):
            return "기획 / 아이디어"
        if any(k in text for k in ["디자인", "미술", "그림", "패션", "일러스트"]):
            return "디자인"
        if any(k in text for k in ["영상", "사진", "숏폼", "미디어", "유튜브"]):
            return "영상 / 콘텐츠"
        if any(k in text for k in ["마케팅", "광고", "홍보", "브랜딩", "PR"]):
            return "마케팅"
        if any(k in text for k in ["창업", "스타트업", "비즈니스", "벤처"]):
            return "창업"
        if any(k in text for k in ["과학", "기술", "공학", "환경"]):
            return "과학 / 기술"
        return "기타"

    def _parse_date(self, date_str: str) -> str:
        """'2026-12-31' 또는 '2026.12.31' 형식 파싱"""
        m = re.search(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', date_str)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
        return (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    def _extract_from_next_data(self, next_data: dict, seen_urls: set, limit: int, results: list) -> None:
        """__NEXT_DATA__ 에서 활동 목록 추출 — 여러 경로 시도"""
        page_props = next_data.get("props", {}).get("pageProps", {})

        # 경로 1: activityItems (공모전 목록)
        for key in ["activityItems", "activities", "contests", "items", "list"]:
            items = page_props.get(key) or []
            if not items and "data" in page_props:
                items = page_props["data"].get(key) or []
            if items:
                for item in items:
                    if len(results) >= limit:
                        return
                    self._process_item(item, seen_urls, results)

        # 경로 2: 중첩된 초기 상태 (Apollo / Redux)
        initial_state = next_data.get("props", {}).get("initialApolloState") or {}
        for key, val in initial_state.items():
            if not isinstance(val, dict):
                continue
            if val.get("__typename") in ["Activity", "Contest", "Supporter"]:
                if len(results) >= limit:
                    return
                self._process_apollo_item(val, seen_urls, results)

    def _process_item(self, item: dict, seen_urls: set, results: list) -> None:
        name = item.get("name") or item.get("title") or ""
        name = name.strip()
        if not name:
            return

        url = item.get("url") or item.get("link") or ""
        if not url:
            slug = item.get("slug") or item.get("id") or ""
            url = f"{self.base_url}/activity/{slug}" if slug else ""
        if not url:
            return
        if not url.startswith("http"):
            url = self.base_url + ("/" if not url.startswith("/") else "") + url
        if url in seen_urls:
            return
        seen_urls.add(url)

        image_url = (
            item.get("imageUrl") or item.get("thumbnail") or
            item.get("image", {}).get("url", "") if isinstance(item.get("image"), dict) else item.get("image") or ""
        )
        if not image_url:
            image_url = "https://linkareer.com/favicon.ico"

        # 마감일
        end_date_raw = (
            item.get("applicationEndDate") or item.get("endDate") or
            item.get("deadline") or item.get("closingDate") or ""
        )
        end_date = self._parse_date(str(end_date_raw)) if end_date_raw else (
            datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        # 태그
        tags = item.get("tags") or item.get("categories") or []
        if isinstance(tags, list):
            tags = [str(t) for t in tags]

        organizer = item.get("organizer") or item.get("organization") or "링커리어 등록 주최사"
        if isinstance(organizer, dict):
            organizer = organizer.get("name", "링커리어 등록 주최사")

        results.append({
            "title": name,
            "organizer": organizer,
            "category": self._normalize_category(name, tags),
            "target_type": "대학생, 청년",
            "description": f"{name} - 링커리어(Linkareer) 실시간 인기 공모전 공고",
            "prize": "시상 혜택 상세페이지 참조",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": end_date,
            "source": "링커리어",
            "source_url": url,
            "thumbnail_url": image_url,
        })

    def _process_apollo_item(self, item: dict, seen_urls: set, results: list) -> None:
        name = item.get("title") or item.get("name") or ""
        if not name:
            return
        slug = item.get("slug") or str(item.get("id") or "")
        if not slug:
            return
        url = f"{self.base_url}/activity/{slug}"
        if url in seen_urls:
            return
        seen_urls.add(url)

        results.append({
            "title": name.strip(),
            "organizer": "링커리어 등록 주최사",
            "category": self._normalize_category(name),
            "target_type": "대학생, 청년",
            "description": f"{name} - 링커리어(Linkareer) 실시간 공모전 공고",
            "prize": "시상 혜택 상세페이지 참조",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "source": "링커리어",
            "source_url": url,
            "thumbnail_url": "https://linkareer.com/favicon.ico",
        })

    def _parse_html_list(self, soup: BeautifulSoup, seen_urls: set, limit: int, results: list) -> None:
        """HTML 직접 파싱 — 링커리어 SSR fallback"""
        selectors = [
            "ul.list > li",
            ".activity-list li",
            ".contest-list li",
            "li[class*='item']",
            "article",
        ]
        items = []
        for sel in selectors:
            found = soup.select(sel)
            if found and len(found) > 1:
                items = found
                break

        for item in items:
            if len(results) >= limit:
                break
            link_elem = item.select_one("a[href]")
            if not link_elem:
                continue
            href = link_elem.get("href", "")
            # 활동 상세 URL만 취급
            if "/activity/" not in href and "/contest/" not in href:
                continue
            url = href if href.startswith("http") else self.base_url + href
            if url in seen_urls:
                continue
            seen_urls.add(url)

            title_elem = item.select_one("h2, h3, h4, strong, .title, .tit, [class*='title']")
            title = title_elem.get_text(strip=True) if title_elem else link_elem.get_text(strip=True)
            if not title or len(title) < 4:
                continue

            img_elem = item.select_one("img")
            thumbnail = ""
            if img_elem:
                thumbnail = img_elem.get("src") or img_elem.get("data-src") or ""
            if not thumbnail:
                thumbnail = "https://linkareer.com/favicon.ico"

            results.append({
                "title": title,
                "organizer": "링커리어 등록 주최사",
                "category": self._normalize_category(title),
                "target_type": "대학생, 청년",
                "description": f"{title} - 링커리어(Linkareer) 실시간 공모전 공고",
                "prize": "시상 혜택 상세페이지 참조",
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "end_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "source": "링커리어",
                "source_url": url,
                "thumbnail_url": thumbnail,
            })

    async def collect(self, limit: int = 80) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_urls: set = set()

        for path in self.LIST_URLS:
            if len(results) >= limit:
                break

            target_url = self.base_url + path
            try:
                resp = await self.client.get(target_url)
                if resp.status_code != 200:
                    print(f"[Linkareer] {path} → {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                before = len(results)

                # 1차: __NEXT_DATA__ 추출
                next_data_elem = soup.find("script", id="__NEXT_DATA__")
                if next_data_elem and next_data_elem.string:
                    try:
                        next_data = json.loads(next_data_elem.string)
                        self._extract_from_next_data(next_data, seen_urls, limit, results)
                    except json.JSONDecodeError:
                        pass

                # 2차: HTML 직접 파싱
                if len(results) == before:
                    self._parse_html_list(soup, seen_urls, limit, results)

                added = len(results) - before
                print(f"[Linkareer] {path}: +{added}개 수집 (누적 {len(results)}개)")

            except Exception as e:
                print(f"[Linkareer] 수집 오류 ({path}): {e}")

        print(f"[Linkareer] 총 {len(results)}개 실제 공모전 수집 완료")
        return results
