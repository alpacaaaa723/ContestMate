import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.collectors.base import BaseCollector


class AllconCollector(BaseCollector):
    """
    올콘 (All-con, https://www.all-con.co.kr) 실제 공모전/대외활동 공식 AJAX API 수집기
    - 공모전(t=1) 및 대외활동(t=2) 다중 페이지네이션
    - 공식 DB query 응답(json)으로 정확한 D-day, 접수기간, 주최기관 수집
    """

    def __init__(self):
        super().__init__(source_name="올콘", base_url="https://www.all-con.co.kr")

    def _normalize_category(self, title: str, raw_cate: str) -> str:
        text = f"{title} {raw_cate}"
        if any(k in text for k in ["AI", "인공지능", "데이터", "빅데이터", "딥러닝", "머신러닝"]):
            return "AI / 인공지능"
        if any(k in text for k in ["웹", "모바일", "IT", "SW", "소프트웨어", "프로그래밍", "개발", "코딩", "해커톤", "보안"]):
            return "IT / 개발"
        if any(k in text for k in ["기획", "아이디어", "전략", "신사업", "정책", "네이밍", "슬로건", "논문"]):
            return "기획 / 아이디어"
        if any(k in text for k in ["디자인", "캐릭터", "웹툰", "일러스트", "포스터", "패키지", "그림", "미술"]):
            return "디자인"
        if any(k in text for k in ["마케팅", "광고", "홍보", "브랜딩", "PR", "서포터즈", "기자단", "앰배서더"]):
            return "마케팅"
        if any(k in text for k in ["영상", "사진", "UCC", "콘텐츠", "유튜브", "숏폼", "촬영", "영화"]):
            return "영상 / 콘텐츠"
        if any(k in text for k in ["창업", "스타트업", "벤처", "비즈니스"]):
            return "창업"
        if any(k in text for k in ["과학", "공학", "기술", "신기술", "R&D", "환경", "건축"]):
            return "과학 / 기술"
        return "기타"

    def _parse_date(self, date_str: str) -> tuple[str, str]:
        """
        '26.11.09~26.11.29' 또는 '2026.11.09 ~ 2026.11.29' 파싱
        """
        today = datetime.now()
        dates = re.findall(r'(\d{2,4})[.\-/](\d{1,2})[.\-/](\d{1,2})', date_str)
        if len(dates) >= 2:
            s_y, s_m, s_d = dates[0]
            e_y, e_m, e_d = dates[1]
            if len(s_y) == 2:
                s_y = f"20{s_y}"
            if len(e_y) == 2:
                e_y = f"20{e_y}"
            start_date = f"{s_y}-{s_m.zfill(2)}-{s_d.zfill(2)}"
            end_date = f"{e_y}-{e_m.zfill(2)}-{e_d.zfill(2)}"
            return start_date, end_date
        elif len(dates) == 1:
            e_y, e_m, e_d = dates[0]
            if len(e_y) == 2:
                e_y = f"20{e_y}"
            end_date = f"{e_y}-{e_m.zfill(2)}-{e_d.zfill(2)}"
            return today.strftime("%Y-%m-%d"), end_date

        return today.strftime("%Y-%m-%d"), (today + timedelta(days=14)).strftime("%Y-%m-%d")

    async def collect(self, limit: int = 80) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_ids = set()
        api_url = f"{self.base_url}/page/ajax.contest_list.php"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base_url}/list/contest/1"
        }

        # t=1: 공모전, t=2: 대외활동
        for t_type in [1, 2]:
            if len(results) >= limit:
                break

            for page in range(1, 6):
                if len(results) >= limit:
                    break

                try:
                    resp = await self.client.post(
                        api_url,
                        data={
                            "page": page,
                            "dataRows": 20,
                            "t": t_type,
                            "sortname": "cl_order",
                            "sortorder": "asc"
                        },
                        headers=headers,
                        timeout=12.0
                    )

                    if resp.status_code != 200:
                        break

                    data = resp.json()
                    rows = data.get("rows", [])
                    if not rows:
                        break

                    added_in_page = 0
                    for row in rows:
                        if len(results) >= limit:
                            break

                        srl = row.get("cl_srl")
                        if not srl or srl in seen_ids:
                            continue
                        seen_ids.add(srl)

                        # HTML 태그 제거하여 제목 파싱
                        raw_title_html = row.get("cl_title", "")
                        soup_title = BeautifulSoup(raw_title_html, "html.parser")
                        title = soup_title.get_text(strip=True)
                        if not title:
                            continue

                        # 주최사
                        host = row.get("cl_host", "").strip() or "올콘 등록 주최사"

                        # 카테고리
                        raw_cate_html = row.get("cl_cate", "")
                        soup_cate = BeautifulSoup(raw_cate_html, "html.parser")
                        cate_text = soup_cate.get_text(" ", strip=True)
                        category = self._normalize_category(title, cate_text)

                        # 날짜
                        date_raw = row.get("cl_date", "")
                        start_date, end_date = self._parse_date(date_raw)

                        source_url = f"{self.base_url}/view/contest/{srl}"
                        thumbnail_url = f"{self.base_url}/images/common/logo.png"

                        results.append({
                            "title": title,
                            "organizer": host,
                            "category": category,
                            "target_type": "대학생, 일반인",
                            "description": f"{title} - 올콘(All-con) 등록 공모전 공고 (주최: {host})",
                            "prize": "상세 공고 참조",
                            "start_date": start_date,
                            "end_date": end_date,
                            "source": "올콘",
                            "source_url": source_url,
                            "thumbnail_url": thumbnail_url
                        })
                        added_in_page += 1

                    if added_in_page == 0:
                        break

                except Exception as e:
                    print(f"[Allcon] Page {page} (type={t_type}) error: {e}")
                    break

        print(f"[Allcon] 총 {len(results)}개 실제 공모전 수집 완료")
        return results
