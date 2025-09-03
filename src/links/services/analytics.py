import hashlib
import time
from datetime import datetime, timezone
from typing import Optional

from django.conf import settings
from django_redis import get_redis_connection

PREFIX = "link"

class LinkAnalytics:
    prefix = PREFIX

    @staticmethod
    def _r():
        return get_redis_connection("default")

    @staticmethod
    def _bucket(ts: Optional[int] = None) -> str:
        dt = datetime.now(timezone.utc) if ts is None else datetime.fromtimestamp(ts, timezone.utc)
        return dt.strftime("%Y%m%d")

    @staticmethod
    def _fingerprint(ip: Optional[str], ua: Optional[str]) -> str:
        base = f"{ip or ''}|{ua or ''}".encode()
        return hashlib.sha1(base).hexdigest()

    @classmethod
    def _key_visits(cls, code: str) -> str:
        return f"{cls.prefix}:{code}:visits"

    @classmethod
    def _key_uv(cls, code: str) -> str:
        return f"{cls.prefix}:{code}:uv"

    @classmethod
    def _key_visits_daily(cls, code: str, bucket: str) -> str:
        return f"{cls.prefix}:{code}:visits:{bucket}"

    @classmethod
    def record_visit(cls, code: str, ip: Optional[str], ua: Optional[str]) -> None:
        r = cls._r()
        r.incr(cls._key_visits(code))
        r.pfadd(cls._key_uv(code), cls._fingerprint(ip, ua))
        daily_key = cls._key_visits_daily(code, cls._bucket())
        r.incr(daily_key)
        r.expire(daily_key, max(1, int(settings.DAILY_BUCKET_TTL)))

    @classmethod
    def get_counts(cls, code: str) -> dict:
        r = cls._r()
        visits = int(r.get(cls._key_visits(code)) or 0)
        uniques = int(r.pfcount(cls._key_uv(code)) or 0)
        return {"visits": visits, "unique_visitors": uniques}

    @classmethod
    def get_daily(cls, code: str, days: int = 30) -> list[dict]:
        r = cls._r()
        out = []
        now = int(time.time())
        for i in range(days):
            ts = now - i * 86400
            bucket = cls._bucket(ts)
            val = int(r.get(cls._key_visits_daily(code, bucket)) or 0)
            out.append({"date": bucket, "visits": val})
        return list(reversed(out))
