from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx


@dataclass
class RobotsResult:
    url: str
    allowed: bool
    status: str
    reason: str


class RobotsCache:
    def __init__(self, user_agent: str, timeout: float = 10.0) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self._cache: dict[str, RobotFileParser | None] = {}

    def can_fetch(self, url: str) -> RobotsResult:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(origin, "/robots.txt")
        parser = self._cache.get(origin)
        if origin not in self._cache:
            parser = self._load_parser(robots_url)
            self._cache[origin] = parser
        if parser is None:
            return RobotsResult(url=url, allowed=False, status="unknown", reason="robots.txt could not be checked")
        allowed = bool(parser.can_fetch(self.user_agent, url))
        return RobotsResult(url=url, allowed=allowed, status="allowed" if allowed else "disallowed", reason=robots_url)

    def _load_parser(self, robots_url: str) -> RobotFileParser | None:
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            response = httpx.get(robots_url, timeout=self.timeout, follow_redirects=True)
        except httpx.HTTPError:
            return None
        if response.status_code == 404:
            parser.parse([])
            return parser
        if response.status_code >= 400:
            return None
        parser.parse(response.text.splitlines())
        return parser
