import time
from typing import Optional
from django.conf import settings
from django_redis import get_redis_connection
from redis import RedisError


REDIS_KEY_NAMESPACE = "link"

class LinkCache:
    """Cache layer for short-link URLs with tombstone support."""

    def __init__(
        self,
        *,
        alias: str = "default",
        prefix: str = REDIS_KEY_NAMESPACE,
        default_ttl: Optional[int] = None,
        tombstone_ttl: Optional[int] = None,
        encoding: str = "utf-8",
    ) -> None:

        self._alias = alias
        self.prefix = prefix
        self.default_ttl = int(
            getattr(settings, "CACHE_DEFAULT_TTL", 86400)
            if default_ttl is None
            else default_ttl
        )
        self.tombstone_ttl = int(
            getattr(settings, "EXPIRED_TOMBSTONE_TTL", 300)
            if tombstone_ttl is None
            else tombstone_ttl
        )
        self.encoding = encoding

    # ---- internal helpers ----
    def _r(self):
        return get_redis_connection(self._alias)

    def _key_url(self, code: str) -> str:
        return f"{self.prefix}:{code}:url"

    def _key_tomb(self, code: str) -> str:
        return f"{self.prefix}:{code}:expired"

    # ---- public ----
    def cache_url(self, code: str, url: str, expire_at_ts: Optional[int]) -> None:
        r = self._r()
        key = self._key_url(code)

        if expire_at_ts is not None:
            now = int(time.time())
            ttl = int(expire_at_ts) - now
            if ttl <= 0:
                # Already expired; don't cache.
                return
            r.set(key, url, ex=ttl)
            return

        if self.default_ttl > 0:
            r.set(key, url, ex=self.default_ttl)
        else:
            r.set(key, url)

    def get_cached_url(self, code: str) -> Optional[str]:
        r = self._r()
        key = self._key_url(code)
        val = r.get(key)
        if val is None:
            return None
        if isinstance(val, (bytes, bytearray)):
            return val.decode(self.encoding, errors="strict")
        return str(val)

    def mark_expired(self, code: str) -> None:
        r = self._r()
        key = self._key_tomb(code)
        ttl = max(1, self.tombstone_ttl)
        r.set(key, 1, ex=ttl)

    def is_tombstoned(self, code: str) -> bool:
        r = self._r()
        key = self._key_tomb(code)
        return bool(r.get(key))

    def uncache_url(self, code: str) -> None:
        r = self._r()
        try:
            r.delete(self._key_url(code))
        except RedisError:
            pass


_default_link_cache = LinkCache()

cache_url = _default_link_cache.cache_url
get_cached_url = _default_link_cache.get_cached_url
mark_expired = _default_link_cache.mark_expired
is_tombstoned = _default_link_cache.is_tombstoned
uncache_url = _default_link_cache.uncache_url
