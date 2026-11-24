import uuid
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from app.collectors.wevity import WevityCollector
from app.collectors.thinkgood import ThinkgoodCollector
from app.collectors.linkareer import LinkareerCollector
from app.collectors.contestkorea import ContestkoreaCollector
from app.collectors.allcon import AllconCollector
from app.collectors.campuspick import CampuspickCollector
from app.collectors.devevent import DevEventCollector
from app.core.database import get_supabase_client, local_db

# 초기 부트스트랩 데이터 (실제 공개 공모전 형태의 고품질 기본 데이터)
DEFAULT_SEED_CONTESTS = [
    {
        "title": "2026 대한민국 생성형 AI 서비스 개발 해커톤",
        "organizer": "과학기술정보통신부 / 정보통신산업진흥원",
        "category": "AI / 인공지능",
        "target_type": "대학생, 대학원생, 일반인",
        "description": "생성형 AI 모델 및 LLM을 활용한 실생활 문제 해결 서비스 개발 대회",
        "prize": "대상 1,000만원 등 총 3,500만원",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "source": "위비티",
        "source_url": "https://www.wevity.com/?c=find&s=1&gbn=view&ix=ai_hackathon_2026",
        "thumbnail_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80"
    },
    {
        "title": "제4회 전국 대학생 IT/웹 오픈소스 개발 경진대회",
        "organizer": "한국소프트웨어산업협회",
        "category": "IT / 개발",
        "target_type": "대학생",
        "description": "클라우드 및 마이크로서비스 기반 실무형 오픈소스 솔루션 기획 및 개발",
        "prize": "대상 500만원 및 네이버클라우드 채용 우대",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "source": "씽굿",
        "source_url": "https://www.thinkcontest.com/Contest/CateProc.html?id=oss_2026",
        "thumbnail_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&auto=format&fit=crop&q=80"
    },
    {
        "title": "2026 청년 창업 아이디어 챌린지 및 사업화 지원",
        "organizer": "중소벤처기업부 / 창업진흥원",
        "category": "창업",
        "target_type": "청년, 대학생, 예비창업자",
        "description": "혁신 비즈니스 모델 발굴 및 초기 시제품 제작 지원금 5,000만원",
        "prize": "사업화 지원금 최대 5,000만원",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
        "source": "링커리어",
        "source_url": "https://linkareer.com/activity/startup_challenge_2026",
        "thumbnail_url": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=600&auto=format&fit=crop&q=80"
    },
    {
        "title": "글로벌 소셜임팩트 브랜딩 & UI/UX 디자인 공모전",
        "organizer": "한국디자인진흥원",
        "category": "디자인",
        "target_type": "대학생, 일반인",
        "description": "친환경/사회혁신 브랜딩 비주얼 아이덴티티 및 모바일 앱 UI/UX 디자인",
        "prize": "총 상금 1,500만원",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "source": "위비티",
        "source_url": "https://www.wevity.com/?c=find&s=1&gbn=view&ix=design_impact_2026",
        "thumbnail_url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&auto=format&fit=crop&q=80"
    },
    {
        "title": "제7회 대학생 디지털 마케팅 & 숏폼 영상 기획전",
        "organizer": "한국마케팅학회",
        "category": "마케팅",
        "target_type": "대학생, 취업준비생",
        "description": "Z세대 대상 바이럴 마케팅 전략 수립 및 숏폼 영상 제작 공모",
        "prize": "대상 300만원 및 인턴십 기회",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
        "source": "씽굿",
        "source_url": "https://www.thinkcontest.com/Contest/CateProc.html?id=marketing_2026",
        "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&auto=format&fit=crop&q=80"
    },
    {
        "title": "2026 빅데이터 기반 도시문제 해결 기획 / 아이디어 공모전",
        "organizer": "서울디지털재단",
        "category": "기획 / 아이디어",
        "target_type": "제한없음",
        "description": "공공 공공데이터를 융합한 스마트 시티 솔루션 정책 아이디어",
        "prize": "서울시장상 및 총 2,000만원",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"), # 오늘 마감
        "source": "링커리어",
        "source_url": "https://linkareer.com/activity/smartcity_ideas_2026",
        "thumbnail_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&auto=format&fit=crop&q=80"
    }
]

class CollectorRunner:
    """
    사이트별 수집기를 순차 또는 병렬 실행하고 DB에 저장하는 오케스트레이터
    """
    def __init__(self):
        self.collectors = [
            WevityCollector(),
            LinkareerCollector(),
            CampuspickCollector(),
            AllconCollector(),
            DevEventCollector(),
            ContestkoreaCollector(),
            ThinkgoodCollector(),
        ]

    def _save_contests(self, items: List[Dict[str, Any]]) -> int:
        supabase = get_supabase_client()
        saved_count = 0
        now_iso = datetime.utcnow().isoformat()

        for item in items:
            source_url = item.get("source_url")
            if not source_url:
                continue

            record = {
                **item,
                "updated_at": now_iso,
                "last_crawled_at": now_iso
            }

            if supabase:
                try:
                    # UPSERT by source_url
                    res = supabase.table("contests").upsert(
                        record, on_conflict="source_url"
                    ).execute()
                    saved_count += 1
                except Exception as e:
                    print(f"[CollectorRunner] Supabase upsert error: {e}")
            else:
                # Local in-memory upsert
                existing_id = None
                for cid, cdata in local_db.contests.items():
                    if cdata.get("source_url") == source_url:
                        existing_id = cid
                        break

                if existing_id:
                    record["id"] = existing_id
                    record["created_at"] = local_db.contests[existing_id].get("created_at")
                    local_db.contests[existing_id] = record
                else:
                    record["id"] = f"contest_{uuid.uuid4().hex[:8]}"
                    record["created_at"] = now_iso
                    local_db.contests[record["id"]] = record
                saved_count += 1

        return saved_count

    def _log_collector_run(self, source: str, status: str, count: int, error_msg: str, started_at: datetime, completed_at: datetime):
        supabase = get_supabase_client()
        log_entry = {
            "id": f"log_{uuid.uuid4().hex[:8]}",
            "source": source,
            "status": status,
            "collected_count": count,
            "error_message": error_msg,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat()
        }

        if supabase:
            try:
                supabase.table("collector_logs").insert(log_entry).execute()
            except Exception as e:
                print(f"[CollectorRunner] Supabase log insert error: {e}")
        else:
            local_db.collector_logs.append(log_entry)

    async def run_all(self) -> Dict[str, Any]:
        """모든 수집기 실행 및 통계 반환"""
        # 먼저 기본 시드 데이터가 비어있다면 자동 적재
        if len(local_db.contests) == 0:
            self._save_contests(DEFAULT_SEED_CONTESTS)

        summary = {}
        for collector in self.collectors:
            started_at = datetime.utcnow()
            status = "SUCCESS"
            err_msg = None
            collected_count = 0

            try:
                # robots.txt 확인
                is_allowed = await collector.check_robots_allowed(collector.base_url)
                if not is_allowed:
                    status = "FAILED"
                    err_msg = "Disallowed by robots.txt"
                    summary[collector.source_name] = {"status": status, "count": 0, "error": err_msg}
                    self._log_collector_run(collector.source_name, status, 0, err_msg, started_at, datetime.utcnow())
                    continue

                items = await collector.collect(limit=120)
                if items:
                    collected_count = self._save_contests(items)
                else:
                    status = "PARTIAL"
                    err_msg = "0 items collected (possible dynamic rendering or anti-scraping policy)"

                summary[collector.source_name] = {
                    "status": status,
                    "count": collected_count,
                    "error": err_msg
                }
            except Exception as e:
                status = "FAILED"
                err_msg = str(e)
                summary[collector.source_name] = {
                    "status": status,
                    "count": 0,
                    "error": err_msg
                }
            finally:
                completed_at = datetime.utcnow()
                self._log_collector_run(collector.source_name, status, collected_count, err_msg, started_at, completed_at)

        return summary

    async def close_all(self):
        for col in self.collectors:
            await col.close()

collector_runner = CollectorRunner()
