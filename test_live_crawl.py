import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.collectors.wevity import WevityCollector
from app.collectors.linkareer import LinkareerCollector
from app.collectors.campuspick import CampuspickCollector
from app.collectors.allcon import AllconCollector
from app.collectors.devevent import DevEventCollector
from app.collectors.contestkorea import ContestkoreaCollector
from app.collectors.thinkgood import ThinkgoodCollector

async def run_all():
    collectors = [
        WevityCollector(),
        LinkareerCollector(),
        CampuspickCollector(),
        AllconCollector(),
        DevEventCollector(),
        ContestkoreaCollector(),
        ThinkgoodCollector(),
    ]

    total = 0
    all_collected = []
    print("=" * 65)
    print("ContestMate 다중 공모전 포털 통합 크롤링 테스트")
    print("=" * 65)

    for c in collectors:
        print(f"\n[{c.source_name}] 수집 시작...")
        try:
            items = await c.collect(limit=100)
            print(f"[{c.source_name}] 수집 완료: {len(items)}개")
            if items:
                print(f"  * 샘플 1: {items[0]['title'][:50]} | 주최: {items[0]['organizer'][:20]} | 마감: {items[0]['end_date']}")
                if len(items) > 1:
                    print(f"  * 샘플 2: {items[1]['title'][:50]} | 주최: {items[1]['organizer'][:20]} | 마감: {items[1]['end_date']}")
            total += len(items)
            all_collected.extend(items)
        except Exception as e:
            print(f"[{c.source_name}] 오류: {e}")
        finally:
            await c.close()

    print("\n" + "=" * 65)
    print(f"전체 수집 합계: {total}개 실제 공모전 / 대회 / 대외활동")
    print("=" * 65)
    return all_collected

if __name__ == "__main__":
    asyncio.run(run_all())
