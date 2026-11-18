import json
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector


class ThinkgoodCollector(BaseCollector):
    """
    씽굿(Thinkgood) 실제 공모전 수집기
    - ld+json 구조화 데이터 + HTML 직접 파싱 병행
    - 여러 카테고리/페이지 순회 지원
    - 실제 포스터 이미지 및 상세 URL 수집
    """

    def __init__(self):
        super().__init__(source_name="씽굿", base_url="https://www.thinkcontest.com")

    def _normalize_category(self, title: str, category_hint: str = "") -> str:
        text = title + " " + category_hint
        if any(k in text for k in ["AI", "인공지능", "데이터", "빅데이터", "딥러닝", "ChatGPT", "GPT"]):
            return "AI / 인공지능"
        if any(k in text for k in ["해커톤", "코딩", "SW", "소프트웨어", "앱", "웹", "개발", "IT", "프로그래밍"]):
            return "IT / 개발"
        if any(k in text for k in ["기획", "아이디어", "전략", "정책", "네이밍", "논문"]):
            return "기획 / 아이디어"
        if any(k in text for k in ["디자인", "캐릭터", "포스터", "일러스트", "미술", "그림", "패키지"]):
            return "디자인"
        if any(k in text for k in ["마케팅", "광고", "PR", "홍보", "서포터즈", "브랜드"]):
            return "마케팅"
        if any(k in text for k in ["영상", "UCC", "숏폼", "사진", "콘텐츠", "유튜브"]):
            return "영상 / 콘텐츠"
        if any(k in text for k in ["창업", "스타트업", "벤처", "비즈니스"]):
            return "창업"
        if any(k in text for k in ["과학", "기술", "공학", "환경", "에너지", "건축"]):
            return "과학 / 기술"
        return "기타"

    def _parse_date_text(self, date_text: str) -> str:
        """'~2026.12.31' 또는 '2026-12-31' 형식 파싱"""
        # ~YYYY.MM.DD 패턴
        m = re.search(r'(\d{4})[.\-](\d{1,2})[.\-](\d{1,2})', date_text)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
        return (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    def _parse_ldjson(self, soup: BeautifulSoup, seen_urls: set, limit: int, results: list) -> None:
        """ld+json ItemList 파싱"""
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string or len(results) >= limit:
                break
            try:
                data = json.loads(script.string)
                # ItemList 형태
                if data.get("@type") == "ItemList" and "itemListElement" in data:
                    for item in data["itemListElement"]:
                        if len(results) >= limit:
                            break
                        name = item.get("name", "").strip()
                        url = item.get("url", "")
                        if not name or not url:
                            continue
                        # 메뉴 링크 제외
                        if any(menu in name for menu in ["공모전", "대외활동", "교육·강연", "씽굿", "Thinkgood"]):
                            continue
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)

                        image_url = item.get("image") or ""
                        if isinstance(image_url, dict):
                            image_url = image_url.get("url", "")
                        if not image_url:
                            image_url = "https://www.thinkcontest.com/images/common/logo.png"

                        results.append({
                            "title": name,
                            "organizer": "씽굿 등록 주최사",
                            "category": self._normalize_category(name),
                            "target_type": "대학생, 일반인",
                            "description": f"{name} - 씽굿(Thinkgood) 실제 등록 공모전 공고",
                            "prize": "상세 페이지 참조",
                            "start_date": datetime.now().strftime("%Y-%m-%d"),
                            "end_date": (datetime.now() + timedelta(days=16)).strftime("%Y-%m-%d"),
                            "source": "씽굿",
                            "source_url": url,
                            "thumbnail_url": image_url,
                        })
            except Exception:
                continue

    def _parse_html_list(self, soup: BeautifulSoup, seen_urls: set, limit: int, results: list) -> None:
        """HTML 직접 파싱 — 씽굿 공모전 목록 카드"""
        # 씽굿 HTML 구조: .contest-list-item, .list-item, li.item, .card 등 여러 패턴 시도
        selectors = [
            "ul.list > li",
            ".contest-list li",
            ".list-wrap li",
            ".contest_list li",
            "li.contest-item",
            ".card-list .card",
        ]
        items = []
        for sel in selectors:
            found = soup.select(sel)
            if found:
                items = found
                break

        for item in items:
            if len(results) >= limit:
                break

            # 제목
            title_elem = item.select_one("a[title], .tit, .title, strong, h3, h4")
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            if not title or len(title) < 4:
                continue

            # URL
            link_elem = item.select_one("a[href]")
            if not link_elem:
                continue
            href = link_elem.get("href", "")
            if href.startswith("http"):
                url = href
            else:
                url = self.base_url + "/" + href.lstrip("/")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # 썸네일
            img_elem = item.select_one("img")
            thumbnail = ""
            if img_elem:
                thumbnail = img_elem.get("src", img_elem.get("data-src", ""))
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = self.base_url + "/" + thumbnail.lstrip("/")
            if not thumbnail:
                thumbnail = "https://www.thinkcontest.com/images/common/logo.png"

            # 마감일
            date_elem = item.select_one(".date, .deadline, .period, .day")
            end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            if date_elem:
                end_date = self._parse_date_text(date_elem.get_text())

            results.append({
                "title": title,
                "organizer": "씽굿 등록 주최사",
                "category": self._normalize_category(title),
                "target_type": "대학생, 일반인",
                "description": f"{title} - 씽굿(Thinkgood) 실제 등록 공모전 공고",
                "prize": "상세 페이지 참조",
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "end_date": end_date,
                "source": "씽굿",
                "source_url": url,
                "thumbnail_url": thumbnail,
            })

    async def collect(self, limit: int = 60) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_urls: set = set()

        # 수집 대상 URL 목록 (메인 + 카테고리 + 페이지네이션)
        urls_to_try = [
            f"{self.base_url}/thinkgood/user/contest/contest-list.do",
            f"{self.base_url}/thinkgood/user/contest/contest-list.do?page=2",
            f"{self.base_url}/thinkgood/user/contest/contest-list.do?page=3",
            f"{self.base_url}",  # 홈페이지
        ]

        for target_url in urls_to_try:
            if len(results) >= limit:
                break
            try:
                resp = await self.client.get(target_url)
                if resp.status_code != 200:
                    print(f"[Thinkgood] {target_url} → {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                before = len(results)

                # 1차: ld+json
                self._parse_ldjson(soup, seen_urls, limit, results)
                # 2차: HTML 직접 파싱
                if len(results) == before:
                    self._parse_html_list(soup, seen_urls, limit, results)

                added = len(results) - before
                print(f"[Thinkgood] {target_url.split('.do')[0].split('/')[-1]}: +{added}개 수집")

            except Exception as e:
                print(f"[Thinkgood] 수집 오류 ({target_url}): {e}")

        print(f"[Thinkgood] 총 {len(results)}개 실제 공모전 수집 완료")
        return results
