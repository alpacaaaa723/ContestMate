from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import urllib.robotparser
import httpx

class BaseCollector(ABC):
    """
    모든 사이트별 수집기가 구현해야 하는 추상 기본 클래스
    """
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            },
            timeout=15.0,
            follow_redirects=True
        )

    async def check_robots_allowed(self, target_url: str) -> bool:
        """robots.txt 규칙을 확인하여 크롤링 가능 여부 판단 (브라우저 User-Agent 적용)"""
        try:
            robots_url = f"{self.base_url.rstrip('/')}/robots.txt"
            resp = await self.client.get(robots_url)
            if resp.status_code == 200:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(resp.text.splitlines())
                return rp.can_fetch("*", target_url)
            return True
        except Exception as e:
            print(f"[{self.source_name}] robots.txt check warning ({e}), defaulting to allow.")
            return True

    @abstractmethod
    async def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    async def close(self):
        await self.client.aclose()
