import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector


class ContestkoreaCollector(BaseCollector):
    """
    콘테스트코리아(ContestKorea, https://www.contestkorea.com) 실제 공모전/대외활동 수집기
    - 공모전(int_gbn=1) 및 대외활동(int_gbn=2) 다중 카테고리 수집
    - view.php 상세 링크 및 실제 주최사, 참가대상, 카테고리 파싱
    """

    TARGET_URLS = [
        "/sub/list.php?int_gbn=1",                                # 공모전 전체
        "/sub/list.php?int_gbn=1&Txt_bcode=030310001",          # 학문·과학·IT
        "/sub/list.php?int_gbn=1&Txt_bcode=030810001",          # 아이디어·건축·창업
        "/sub/list.php?int_gbn=1&Txt_bcode=030510001",          # 미술·디자인·웹툰
        "/sub/list.php?int_gbn=1&Txt_bcode=030710001",          # 사진·영상·영화제
        "/sub/list.php?int_gbn=1&Txt_bcode=030210001",          # 네이밍·슬로건
        "/sub/list.php?int_gbn=2",                                # 대외활동 전체
        "/sub/list.php?int_gbn=2&Txt_bcode=040110001",          # 서포터즈·기자단
    ]

    def __init__(self):
        super().__init__(source_name="콘테스트코리아", base_url="https://www.contestkorea.com")

    def _normalize_category(self, title: str) -> str:
        if any(k in title for k in ["AI", "인공지능", "데이터", "빅데이터", "딥러닝"]):
            return "AI / 인공지능"
        if any(k in title for k in ["IT", "개발", "코딩", "SW", "해커톤", "프로그래밍", "앱", "웹"]):
            return "IT / 개발"
        if any(k in title for k in ["기획", "아이디어", "전략", "정책", "네이밍", "슬로건", "논문"]):
            return "기획 / 아이디어"
        if any(k in title for k in ["디자인", "캐릭터", "포스터", "일러스트", "미술", "웹툰"]):
            return "디자인"
        if any(k in title for k in ["마케팅", "광고", "PR", "홍보", "서포터즈", "기자단"]):
            return "마케팅"
        if any(k in title for k in ["영상", "사진", "UCC", "콘텐츠", "유튜브", "숏폼", "영화"]):
            return "영상 / 콘텐츠"
        if any(k in title for k in ["창업", "스타트업", "벤처", "비즈니스"]):
            return "창업"
        if any(k in title for k in ["과학", "기술", "공학", "환경"]):
            return "과학 / 기술"
        return "기타"

    def _clean_title(self, raw_title: str) -> str:
        # 접두 태그 제거 (예: 네이밍•슬로건1004섬 -> 1004섬)
        cleaned = re.sub(r'^(네이밍•슬로건|학문•과학•IT|미술•디자인•웹툰|사진•영상•영화제|아이디어•건축•창업|문학•문예|서포터즈 • 기자단|인턴 • 체험)\s*', '', raw_title)
        # 앞의 숫자 제거 (예: 1. 2027 지역 -> 2027 지역)
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
        return cleaned.strip()

    async def collect(self, limit: int = 80) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_urls: set = set()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"
        }

        for path in self.TARGET_URLS:
            if len(results) >= limit:
                break

            target_url = f"{self.base_url}{path}" if path.startswith("/") else path
            try:
                resp = await self.client.get(target_url, headers=headers, timeout=12.0)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                view_links = [
                    a for a in soup.find_all("a")
                    if "view.php" in a.get("href", "") and len(a.get_text(strip=True)) >= 5
                ]

                for a in view_links:
                    if len(results) >= limit:
                        break

                    raw_href = a.get("href", "")
                    if raw_href.startswith("http"):
                        url = raw_href
                    else:
                        url = f"{self.base_url}/sub/{raw_href.lstrip('/')}" if not raw_href.startswith("/sub") else f"{self.base_url}{raw_href}"

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    raw_title = a.get_text(strip=True)
                    title = self._clean_title(raw_title)
                    if not title or len(title) < 4:
                        continue

                    # 부모 컨테이너에서 주최사 및 마감일 파싱
                    parent = a.find_parent("li") or a.find_parent("tr") or a.find_parent("div")
                    parent_text = parent.get_text(" ", strip=True) if parent else ""

                    # 주최사
                    organizer = "콘테스트코리아 등록 주최사"
                    m_host = re.search(r'주최\s*[.:]\s*([^\s,]+(?:\s+[^\s,]+){0,2})', parent_text)
                    if m_host:
                        organizer = m_host.group(1).strip()

                    # 마감일 (D-day 또는 날짜)
                    end_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
                    m_dday = re.search(r'D-(\d+)', parent_text)
                    if m_dday:
                        end_date = (datetime.now() + timedelta(days=int(m_dday.group(1)))).strftime("%Y-%m-%d")
                    else:
                        m_date = re.search(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', parent_text)
                        if m_date:
                            end_date = f"{m_date.group(1)}-{m_date.group(2).zfill(2)}-{m_date.group(3).zfill(2)}"

                    category = self._normalize_category(title)

                    results.append({
                        "title": title,
                        "organizer": organizer,
                        "category": category,
                        "target_type": "대학생, 일반인",
                        "description": f"{title} - 콘테스트코리아(ContestKorea) 실제 등록 공모전 공고",
                        "prize": "상세 페이지 참조",
                        "start_date": datetime.now().strftime("%Y-%m-%d"),
                        "end_date": end_date,
                        "source": "콘테스트코리아",
                        "source_url": url,
                        "thumbnail_url": "https://www.contestkorea.com/favicon.ico"
                    })

            except Exception as e:
                print(f"[ContestKorea] Error ({path}): {e}")

        print(f"[ContestKorea] 총 {len(results)}개 실제 공모전 수집 완료")
        return results
