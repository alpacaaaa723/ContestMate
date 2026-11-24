import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.collectors.base import BaseCollector


class DevEventCollector(BaseCollector):
    """
    데브이벤트 (Dev-Event, https://github.com/brave-people/Dev-Event)
    - 국내 대표 IT / SW / AI 개발자 대회, 해커톤, 프롬프톤, 컨퍼런스 실시간 큐레이션
    - 공식 저장소 Markdown 데이터 기반 안정적/대량 수집
    """

    RAW_URL = "https://raw.githubusercontent.com/brave-people/Dev-Event/master/README.md"

    def __init__(self):
        super().__init__(source_name="데브이벤트", base_url="https://dev-event.vercel.app")

    def _normalize_category(self, title: str, tags: str) -> str:
        text = f"{title} {tags}"
        if any(k in text for k in ["AI", "인공지능", "데이터", "머신러닝", "딥러닝", "LLM", "GPT", "프롬프트"]):
            return "AI / 인공지능"
        if any(k in text for k in ["해커톤", "대회", "챌린지", "코딩", "SW", "개발", "웹", "앱", "클라우드", "보안"]):
            return "IT / 개발"
        if any(k in text for k in ["아이디어", "기획"]):
            return "기획 / 아이디어"
        if any(k in text for k in ["디자인", "UI", "UX"]):
            return "디자인"
        if any(k in text for k in ["스타트업", "창업"]):
            return "창업"
        return "IT / 개발"

    def _parse_dates(self, date_line: str) -> tuple[str, str]:
        today = datetime.now()
        current_year = today.year

        # 패턴: MM. DD ~ MM. DD 또는 YYYY. MM. DD
        matches = re.findall(r'(\d{1,4})[.\-/]\s*(\d{1,2})(?:[.\-/]\s*(\d{1,2}))?', date_line)
        if len(matches) >= 2:
            # 뒷부분이 종료일
            m_end = matches[-1]
            if len(m_end) == 3 and m_end[2]:
                end_year = int(m_end[0]) if len(m_end[0]) == 4 else current_year
                end_month = int(m_end[1])
                end_day = int(m_end[2])
            else:
                end_year = current_year
                end_month = int(m_end[0])
                end_day = int(m_end[1])
            try:
                end_date = datetime(end_year, end_month, end_day).strftime("%Y-%m-%d")
                return today.strftime("%Y-%m-%d"), end_date
            except Exception:
                pass

        return today.strftime("%Y-%m-%d"), (today + timedelta(days=21)).strftime("%Y-%m-%d")

    async def collect(self, limit: int = 80) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_urls = set()

        try:
            resp = await self.client.get(self.RAW_URL, timeout=15.0)
            if resp.status_code != 200:
                print(f"[DevEvent] Status: {resp.status_code}")
                return results

            lines = resp.text.split("\n")
            current_item = None

            for line in lines:
                if len(results) >= limit:
                    break

                stripped = line.strip()

                # 새 이벤트 시작: - __[제목](URL)__
                m_title = re.match(r'-\s*__\[(.*?)\]\((.*?)\)__', stripped)
                if m_title:
                    if current_item and current_item.get("title") and current_item.get("source_url"):
                        results.append(current_item)
                        seen_urls.add(current_item["source_url"])

                    title = m_title.group(1).strip()
                    url = m_title.group(2).strip()

                    if url in seen_urls:
                        current_item = None
                        continue

                    current_item = {
                        "title": title,
                        "organizer": "IT 개발 커뮤니티 / 주최사",
                        "category": self._normalize_category(title, ""),
                        "target_type": "대학생, 개발자, 일반인",
                        "description": f"{title} - 실무 개발자 및 대학생 대상 테크 대회/이벤트",
                        "prize": "상세 링크 참조",
                        "start_date": datetime.now().strftime("%Y-%m-%d"),
                        "end_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
                        "source": "데브이벤트",
                        "source_url": url,
                        "thumbnail_url": "https://raw.githubusercontent.com/brave-people/Dev-Event/master/static/images/logo.png"
                    }
                    continue

                if current_item:
                    # 분류 태그
                    if "분류:" in stripped:
                        tags = stripped.replace("분류:", "").replace("`", "")
                        current_item["category"] = self._normalize_category(current_item["title"], tags)
                    # 주최
                    elif "주최:" in stripped:
                        org = stripped.replace("주최:", "").strip()
                        if org:
                            current_item["organizer"] = org
                    # 접수 기간
                    elif "접수:" in stripped or "일시:" in stripped:
                        s_d, e_d = self._parse_dates(stripped)
                        current_item["start_date"] = s_d
                        current_item["end_date"] = e_d

            if current_item and current_item.get("title") and len(results) < limit:
                results.append(current_item)

        except Exception as e:
            print(f"[DevEvent] Collection error: {e}")

        print(f"[DevEvent] 총 {len(results)}개 실제 개발/AI 공모전 수집 완료")
        return results
