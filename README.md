# Narco Empire

> **Underground logistics & distribution network simulator.**
> A joke project — nothing criminal, just for fun.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Client                          │
│          React SPA (Vite) → Nginx (:80)             │
└────────────┬───────────────────────────┬────────────┘
             │ /market/*                 │ /user/*
             ▼                           ▼
┌──────────────────────┐   ┌──────────────────────┐
│   Market Service     │   │    User Service       │
│   FastAPI (:8000)    │   │   FastAPI (:8001)     │
│   PostgreSQL         │   │   PostgreSQL          │
│   GeoIP + Currency   │   │   User registration   │
└────────┬─────────────┘   └──────────────────────┘
         │ Redis
         ▼
┌──────────────────────┐
│       Redis          │
│   Currency cache     │
│   Country codes      │
└────────┬─────────────┘
         │
┌────────▼─────────────┐
│   Celery Beat        │
│   (currency refresh  │
│    every 3600s)      │
└──────────────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Market API | `:8000` | Product CRUD, geo-based currency conversion |
| User API | `:8001` | User registration with card numbers |
| Redis | `:6379` | Currency rates cache, per-user session data |
| Celery Worker | — | Refreshes FX rates from CurrencyFreaks API |
| Celery Beat | — | Schedules refresh every hour |
| Frontend | `:80` | React SPA served via Nginx |
| PostgreSQL | `:5432` | Persistent storage (market + user DBs) |

### Tech Stack

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy (async), Alembic
- **Frontend:** React 19, React Router 7, Vite 6
- **Queue:** Celery + Redis (broker)
- **Infra:** Docker Compose, Nginx, PostgreSQL, Redis
- **Integrations:** CurrencyFreaks API, GeoIP2 (MaxMind), ipify.org

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- GeoLite2-Country.mmdb file (place in project root)

### Run

```bash
docker compose up --build
```

- Frontend: http://localhost
- Market API: http://localhost:8000/docs
- User API: http://localhost:8001/docs

### Development (without Docker)

```bash
# Backend
uv venv
source .venv/bin/activate
uv sync

# Market service
uvicorn app.main:app --reload --port 8000

# User service
uvicorn user_app.main:app --reload --port 8001

# Celery worker (in separate terminal)
celery -A celery_app.currency worker --loglevel=INFO
celery -A celery_app.currency beat --loglevel=INFO

# Frontend
cd frontend
npm install
npm run dev
```

> Frontend dev server at http://localhost:5173 proxies `/market` → `:8000` and `/user` → `:8001`.

---

## API Reference

### Market Service

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/market/product` | Create product |
| `GET` | `/market/product?id=N` | Get product by ID (with currency conversion) |
| `GET` | `/market/products` | List all products |

**POST /market/product**

```json
{ "title": "Colombian Gold", "price": 99.99 }
```

**GET /market/product?id=1** — Returns product price converted to user's local currency
based on IP geolocation and live FX rates.

### User Service

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/user/register` | Register new user |

**POST /user/register**

```json
{ "username": "el_patron", "card_number": 1234567890123456 }
```

---

## Project Structure

```
.
├── app/                    # Market service
│   ├── main.py             # FastAPI app, CORS, middleware
│   ├── models.py           # SQLAlchemy models (ProductModel)
│   ├── schemas.py          # Pydantic validation
│   ├── routers.py          # API endpoints
│   ├── databases.py        # DB engine & sessions
│   ├── middleware/
│   │   └── ip_address.py   # RealIP extraction (Cloudflare, Nginx)
│   ├── alembic/            # DB migrations
│   └── Dockerfile
├── user_app/               # User service (microservice)
│   ├── main.py
│   ├── models.py           # UserModel
│   ├── schemas.py          # UserValidation
│   ├── routers.py          # Register endpoint
│   ├── databases.py
│   ├── enums.py            # RoleEnum
│   └── Dockerfile
├── celery_app/
│   └── currency.py         # Celery tasks for FX rate refresh
├── frontend/               # React SPA
│   ├── src/
│   │   ├── App.jsx         # Routes
│   │   ├── main.jsx        # Entry point
│   │   ├── api/client.js   # HTTP client
│   │   ├── components/
│   │   │   └── Layout.jsx  # Nav + shell
│   │   └── pages/
│   │       ├── Home.jsx        # Landing
│   │       ├── Products.jsx    # Inventory list + search
│   │       ├── CreateProduct.jsx
│   │       └── Register.jsx
│   └── Dockerfile
├── tests/
│   ├── conftest.py         # Fixtures (mocked DB, Redis)
│   ├── test_app.py         # Market API tests
│   └── test_user_app.py    # User API tests
├── docker-compose.yml
├── ngnix.conf              # Production Nginx config
└── pyproject.toml
```

---

## Key Design Decisions

### Microservices
Market and User are separate FastAPI processes, each with its own database schema.
They can be scaled independently. Communication via HTTP (future: RabbitMQ via FastStream,
already in dependencies).

### Currency Conversion
- MaxMind GeoIP2 database maps IP → country
- Redis stores `country → currency_code` mapping
- Celery fetches live FX rates from CurrencyFreaks every hour
- Product prices shown in user's local currency

### Highload Considerations
- Async SQLAlchemy + asyncpg for non-blocking DB access
- Redis caching (currency per user, 8h TTL)
- Connection pooling (pool_size=5, max_overflow=10)
- Nginx reverse proxy with gzip + caching
- Each service independently scalable via Docker

---

## Testing

```bash
pytest -v
```

Tests use mocked DB sessions and Redis — no external dependencies required.
