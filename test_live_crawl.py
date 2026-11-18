"""
ContestMate 실제 크롤링 대용량 테스트
위비티 최대 120개, 씽굿 최대 60개, 링커리어 최대 80개 목표
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.collectors.wevity import WevityCollector
from app.collectors.thinkgood import ThinkgoodCollector
from app.collectors.linkareer import LinkareerCollector


async def run_all():
    total = 0
    print("=" * 60)
    print("ContestMate 대용량 크롤링 테스트")
    print("=" * 60)

    for CollectorClass in [WevityCollector, ThinkgoodCollector, LinkareerCollector]:
        c = CollectorClass()
        print(f"\n{'─' * 40}")
        print(f"[{c.source_name}] 수집 시작...")
        try:
            items = await c.collect()
            print(f"[{c.source_name}] 수집 완료: {len(items)}개")
            if items:
                print(f"  예시 1: {items[0]['title'][:50]} | 마감: {items[0]['end_date']}")
                if len(items) > 1:
                    print(f"  예시 2: {items[1]['title'][:50]} | 마감: {items[1]['end_date']}")
                if len(items) > 2:
                    print(f"  예시 3: {items[2]['title'][:50]} | 마감: {items[2]['end_date']}")
            total += len(items)
        except Exception as e:
            print(f"[{c.source_name}] 오류: {e}")
        finally:
            await c.client.aclose()

    print(f"\n{'=' * 60}")
    print(f"전체 수집 합계: {total}개 실제 공모전")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all())
