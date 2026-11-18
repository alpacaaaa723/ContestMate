import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector


class ContestkoreaCollector(BaseCollector):
    """
    콘테스트코리아(ContestKorea) 실제 공모전 수집기
    - 대회·공모전 / 대외활동 카테고리 순회
    - div.list 구조 HTML 파싱
    - 전국 단위 공모전 다량 수집
    """

    # 카테고리 URL 목록 (대회·공모전)
    CONTEST_URLS = [
        "/sub/list.php?int_gbn=1&Txt_bcode=030110001",  # 문학·문예
        "/sub/list.php?int_gbn=1&Txt_bcode=030210001",  # 네이밍·슬로건
        "/sub/list.php?int_gbn=1&Txt_bcode=030310001",  # 학문·과학·IT
        "/sub/list.php?int_gbn=1&Txt_bcode=030410001",  # 스포츠
        "/sub/list.php?int_gbn=1&Txt_bcode=030510001",  # 미술·디자인·웹툰
        "/sub/list.php?int_gbn=1&Txt_bcode=030610001",  # 음악·콩쿠르·댄스
        "/sub/list.php?int_gbn=1&Txt_bcode=030710001",  # 사진·영상·영화제
        "/sub/list.php?int_gbn=1&Txt_bcode=030810001",  # 아이디어·건축·창업
        "/sub/list.php?int_gbn=2&Txt_bcode=040110001",  # 서포터즈·기자단
        "/sub/list.php",                                 # 전체
    ]

    CATEGORY_CODE_MAP = {
        "030110001": "기타",
        "030210001": "기획 / 아이디어",
        "030310001": "과학 / 기술",
        "030410001": "기타",
        "030510001": "디자인",
        "030610001": "기타",
        "030710001": "영상 / 콘텐츠",
        "030810001": "창업",
        "040110001": "마케팅",
    }

    def __init__(self):
        super().__init__(source_name="콘테스트코리아", base_url="https://www.contestkorea.com")

    def _normalize_category(self, title: str, hint: str = "") -> str:
        text = title + " " + hint
        if any(k in text for k in ["AI", "인공지능", "데이터", "빅데이터", "ChatGPT", "GPT", "딥러닝"]):
            return "AI / 인공지능"
        if any(k in text for k in ["IT", "개발", "코딩", "SW", "해커톤", "프로그래밍", "앱", "웹"]):
            return "IT / 개발"
        if any(k in text for k in ["기획", "아이디어", "전략", "정책", "네이밍", "슬로건", "논문"]):
            return "기획 / 아이디어"
        if any(k in text for k in ["디자인", "캐릭터", "포스터", "일러스트", "미술", "웹툰", "그림", "패키지"]):
            return "디자인"
        if any(k in text for k in ["마케팅", "광고", "PR", "홍보", "서포터즈", "기자단", "앰배서더"]):
            return "마케팅"
        if any(k in text for k in ["영상", "사진", "UCC", "콘텐츠", "유튜브", "숏폼", "촬영", "영화"]):
            return "영상 / 콘텐츠"
        if any(k in text for k in ["창업", "스타트업", "벤처", "비즈니스", "아이디어"]):
            return "창업"
        if any(k in text for k in ["과학", "기술", "공학", "환경", "에너지", "건축", "수학", "물리"]):
            return "과학 / 기술"
        return "기타"

    def _parse_date(self, date_str: str) -> str:
        """날짜 텍스트에서 YYYY-MM-DD 추출"""
        m = re.search(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', date_str)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
        # 'D-숫자' 형식
        m2 = re.search(r'D-(\d+)', date_str)
        if m2:
            return (datetime.now() + timedelta(days=int(m2.group(1)))).strftime("%Y-%m-%d")
        return (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    def _parse_page(self, soup: BeautifulSoup, seen_urls: set, limit: int, results: list, cat_hint: str = "") -> None:
        """div.list 구조 파싱"""
        list_divs = soup.select("div.list")
        for div in list_divs:
            if len(results) >= limit:
                break

            # 제목 링크
            link_elem = div.select_one("a[href*='view.php']")
            if not link_elem:
                continue

            href = link_elem.get("href", "")
            url = href if href.startswith("http") else self.base_url + "/" + href.lstrip("/")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            title_elem = div.select_one(".contest_title, strong, b, .tit, h4, h3")
            if not title_elem:
                # fallback: 링크 텍스트
                raw_title = link_elem.get_text(strip=True)
            else:
                raw_title = title_elem.get_text(strip=True)

            title = raw_title.strip()
            if not title or len(title) < 4:
                continue

            # 주최기관
            organizer_elem = div.select_one(".organ, .organizer, .host, .company")
            organizer = organizer_elem.get_text(strip=True) if organizer_elem else "콘테스트코리아 등록 주최사"

            # 썸네일
            img_elem = div.select_one("img")
            thumbnail = ""
            if img_elem:
                thumbnail = img_elem.get("src", img_elem.get("data-src", ""))
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = self.base_url + "/" + thumbnail.lstrip("/")
            if not thumbnail:
                thumbnail = "https://www.contestkorea.com/favicon.ico"

            # 마감일
            date_elem = div.select_one(".deadline, .date, .period, .day, [class*='date']")
            end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            if date_elem:
                end_date = self._parse_date(date_elem.get_text())

            results.append({
                "title": title,
                "organizer": organizer if organizer else "콘테스트코리아 등록 주최사",
                "category": self._normalize_category(title, cat_hint),
                "target_type": "대학생, 일반인",
                "description": f"{title} - 콘테스트코리아(ContestKorea) 실제 등록 공모전 공고",
                "prize": "상세 페이지 참조",
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "end_date": end_date,
                "source": "콘테스트코리아",
                "source_url": url,
                "thumbnail_url": thumbnail,
            })

    async def collect(self, limit: int = 60) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_urls: set = set()

        for path in self.CONTEST_URLS:
            if len(results) >= limit:
                break

            target_url = self.base_url + path
            # 카테고리 힌트 추출
            cat_code = ""
            m = re.search(r'Txt_bcode=(\d+)', path)
            if m:
                cat_code = m.group(1)
            cat_hint = self.CATEGORY_CODE_MAP.get(cat_code, "")

            try:
                resp = await self.client.get(target_url)
                if resp.status_code != 200:
                    print(f"[콘테스트코리아] {path[:40]} → {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                before = len(results)
                self._parse_page(soup, seen_urls, limit, results, cat_hint)
                added = len(results) - before
                print(f"[콘테스트코리아] {path[:40]}: +{added}개 (누적 {len(results)}개)")

            except Exception as e:
                print(f"[콘테스트코리아] 오류 ({path[:40]}): {e}")

        print(f"[콘테스트코리아] 총 {len(results)}개 실제 공모전 수집 완료")
        return results
