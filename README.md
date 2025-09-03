# URL Shortener — Django/DRF + PostgreSQL + Redis + JWT (Dockerized)

A production‑lean URL shortener with **expiration**, **Redis caching/analytics**, and **JWT‑based auth**. Containerized with **Docker Compose** (Django web, PostgreSQL, Redis). Optional **Celery** worker/beat for periodic cleanup.

---

## Features
- **Short links** with **Base62** short codes derived from DB IDs
- **Expiration** per link; expired links return **HTTP 410 Gone**
- **High‑speed redirects** via Redis cache (`code → url`) and **tombstones** for expired keys
- **Analytics** (Redis):
  - **Total visits** (atomic `INCR`)
  - **Unique visitors** (HyperLogLog `PFADD/PFCOUNT`, memory‑efficient)
  - Optional **daily buckets** for simple time‑series counts
- **Authentication**: Custom **User** (email as username) + **JWT** (SimpleJWT)
- **API Docs**: OpenAPI/Swagger via `drf-spectacular`
- **Docker Compose**: 3 core services (web, db, redis) + optional celery/beat
- **Tests**: Basic API tests (create/link, redirect, expiration)

> **Redis note**: We use `SET` with options (e.g., `ex=`) instead of `SETEX`. Since Redis ≥ 2.6.12 supports this, there’s no reason to stick to `SETEX`/`PSETEX`/`SETNX`.

---

## Architecture
```
Client → DRF API (Django)
                  ├── PostgreSQL (links, users)
                  └── Redis (cache, tombstones, counters, HLL uniques)

(Optional) Celery worker/beat → scheduled cleanup of expired links + Redis keys
```

---

## Directory Layout
```
root
|   .env.example
|   .gitignore
|   docker-compose.yml
|   LICENSE
|   README.md

|   
+---src
|   |   .dockerignore
|   |   db.sqlite3
|   |   Dockerfile
|   |   entrypoint.sh
|   |   manage.py
|   |   requirements.txt
|   |   
|   +---accounts
|   |   |   admin.py
|   |   |   apps.py
|   |   |   managers.py
|   |   |   models.py
|   |   |   serializers.py
|   |   |   tests.py
|   |   |   urls.py
|   |   |   views.py
|   |   |   __init__.py
|   |   |   
|   |   | 
|   +---config
|   |   |   asgi.py
|   |   |   celery.py
|   |   |   settings.py
|   |   |   urls.py
|   |   |   wsgi.py
|   |   |   __init__.py
|   |   |   
|   |           
|   \---links
|       |   admin.py
|       |   apps.py
|       |   helpers.py
|       |   mixins.py
|       |   models.py
|       |   serializers.py
|       |   tasks.py
|       |   tests.py
|       |   urls.py
|       |   views.py
|       |   __init__.py
|       |   
|       |           
|       +---services
|       |   |   analytics.py
|       |   |   base62.py
|       |   |   cache.py
|       |   |   __init__.py
|       |   | 
```

---

## Stack
- **Runtime**: Python 3.12, Django 5, DRF
- **DB**: PostgreSQL 16 (Alpine)
- **Cache/Analytics**: Redis 7 (Alpine) + `django-redis`
- **Auth**: Custom `accounts.User` (email login) + `rest_framework_simplejwt`
- **Docs**: `drf-spectacular` (Swagger UI)
- **Async (optional)**: Celery 5 + Redis broker/result backend

---

## Quickstart (Docker Compose)
1) Copy environment file and adjust values:
```bash
cp .env.example .env
```

2) Build & start services:
```bash
docker compose up --build
```
By default, the Django app runs on `http://localhost:8000`.

3) (Optional) Create a superuser to access Django admin:
```bash
docker compose exec web python manage.py createsuperuser
```

4) API Docs:
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

5) (Optional) Celery worker & beat:
```bash
docker compose -f docker-compose.yml -f docker-compose.celery.override.yml up --build
```

> Migrations run automatically in `entrypoint.sh` on container boot. Re‑run manually if needed: `docker compose exec web python manage.py migrate`.

---

## Configuration (.env)
```env
# Django
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=please-change-me
DJANGO_ALLOWED_HOSTS=*
BASE_URL=http://localhost:8000

# PostgreSQL
POSTGRES_DB=urlshort
POSTGRES_USER=urlshort
POSTGRES_PASSWORD=urlshort
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Cache/Analytics TTLs (seconds)
CACHE_DEFAULT_TTL=604800        # default TTL for cached urls without expire_at (7d)
EXPIRED_TOMBSTONE_TTL=21600     # tombstone TTL for expired links (6h)
DAILY_BUCKET_TTL=7776000        # daily visit counters retention (90d)

# JWT lifetimes
ACCESS_TOKEN_LIFETIME_MIN=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

---

## Authentication (accounts)
Custom user model with **email** as username. JWT tokens via SimpleJWT.

**Endpoints**
- `POST /api/accounts/register/`
  - Body: `{ "email", "password", "first_name?", "last_name?" }`
  - 201 Created → `{ "detail": "registered" }`
- `POST /api/token/`
  - Body: `{ "email", "password" }`
  - 200 OK → `{ "access", "refresh" }`
- `POST /api/token/refresh/`
  - Body: `{ "refresh" }`
  - 200 OK → `{ "access" }`
- `GET /api/accounts/me/` (Bearer token)
  - 200 OK → `{ "id", "email", "first_name", "last_name", "date_joined" }`
- `POST /api/accounts/password-change/` (Bearer token)
  - Body: `{ "old_password", "new_password" }`
  - 200 OK → `{ "detail": "password-updated" }`

**Auth header**
```
Authorization: Bearer <ACCESS_TOKEN>
```

---

## URL Shortener (links)
**Create short link**
- `POST /api/links/`
- Body: `{ "original_url": "https://example.com", "expire_at?": "2030-01-01T00:00:00Z" }`
- 201 Created → `{ "code", "original_url", "expire_at", "short_url", "created_at" }`

**Redirect**
- `GET /r/{code}`
  - Valid → **302** to `original_url`
  - Expired → **410 Gone**
  - Not found → **404 Not Found**

**List my links** (requires JWT)
- `GET /api/links/` → paginated results (PageNumberPagination; `page` query param)

**Analytics**
- `GET /api/links/{code}/analytics?daily=true|false`
- Response: `{ "code", "visits", "unique_visitors", "daily?": [{"date":"YYYYMMDD","visits":N}, ...] }`

---

## Implementation Notes
- **Base62 codes**: Derived from auto‑incrementing primary keys → compact and unique. For non‑guessable codes, add salt/random suffix.
- **Expiration**: `expire_at` checked at redirect; Redis cache TTL mirrors expiration when present. Expired keys leave a **tombstone** to short‑circuit DB hits.
- **Uniques**: HyperLogLog (`PFADD/PFCOUNT`) keeps memory use small; if exact cardinality is mandatory, switch to a Redis `SET` at higher memory cost.
- **Client IP**: Trusts `X-Forwarded-For` when behind a proxy; configure proxy headers properly in production.

---

## Production Hardening
- Run under **Gunicorn** behind **Nginx** (HTTPS/HTTP2, gzip/br)
- Set secure Django settings: `DEBUG=False`, proper `ALLOWED_HOSTS`, `SECURE_` headers, CSRF settings for any browser‑based flows
- Externalize **SECRET_KEY** and database credentials
- Consider **CORS** if serving a separate frontend (e.g., `django-cors-headers`)
- Add **rate limiting** (DRF throttling or gateway rate‑limit) for create/redirect endpoints
- Turn on persistence/backups for PostgreSQL and monitor Redis memory/evictions

---

## cURL Examples
Create a link:
```bash
curl -X POST http://localhost:8000/api/links/ \
  -H 'Content-Type: application/json' \
  -d '{"original_url": "https://www.djangoproject.com/", "expire_at": "2030-01-01T00:00:00Z"}'
```

Register → Login → Me:
```bash
curl -X POST http://localhost:8000/api/accounts/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"StrongPass!123"}'

curl -X POST http://localhost:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"StrongPass!123"}'
# → {"access":"...","refresh":"..."}

curl http://localhost:8000/api/accounts/me \
  -H "Authorization: Bearer <ACCESS>"
```

Analytics:
```bash
curl http://localhost:8000/api/links/<code>/analytics?daily=true
```

---

## Troubleshooting
- **Redis errors**: check `REDIS_URL` and container health; ensure network works between `web` and `redis` services.
- **DB auth errors**: make sure `.env` DB creds match `docker-compose.yml` envs; inspect `db` logs.
- **Unexpected 410**: verify system clock / timezone and `expire_at` correctness (containers are UTC by default).
- **Swagger 404**: confirm `drf-spectacular` installed and routes in `config/urls.py`.

---

## License
MIT.

