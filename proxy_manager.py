import random
import time
from typing import Dict, List, Optional

class ProxyManager:
    def __init__(self, proxies: List[str], cooldown: float = 60.0):
        """
        proxies: list of proxy URLs, e.g. http://user:pass@ip:port
        cooldown: seconds a proxy is sidelined after failure
        """
        self.cooldown = cooldown
        self._pool: Dict[str, float] = {p: 0.0 for p in proxies}

    def get_proxy(self) -> Optional[str]:
        now = time.time()
        available = [p for p, t in self._pool.items() if t <= now]
        return random.choice(available) if available else None

    def mark_bad(self, proxy: str):
        self._pool[proxy] = time.time() + self.cooldown

    def has_available(self) -> bool:
        now = time.time()
        return any(t <= now for t in self._pool.values())
