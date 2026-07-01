# Empire Market

Highload marketplace simulator. A joke project — just for fun and architectural exploration.

---

## Purpose

Simulate a distributed marketplace with inventory (geo-localized pricing), orders, payments, and pickup points. Built for horizontal scale — targeting millions of simulated users via AI-driven load testing.

The real product is the architecture itself: async microservices, message-driven orchestration, multi-layer caching, and Kubernetes-native deployment.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                     Client Layer                          │
│           React SPA ── Nginx (:80)                        │
│              (Vite dev :5173)                              │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                   API Gateway (Nginx)                     │
│              /market/* → :8000   /user/* → :8001          │
│              /orders/* → :8002   /payments/* → :8003      │
└──┬──────────┬──────────┬──────────┬──────────────────────┘
   │          │          │          │
   ▼          ▼          ▼          ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│Market│ │User  │ │Order │ │Payment   │
│:8000 │ │:8001 │ │:8002 │ │:8003     │
│Fast  │ │Fast  │ │Fast  │ │FastAPI   │
│API   │ │API   │ │API   │ │          │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───────┘
   │        │        │        │
   │        │   ┌────▼────┐   │
   │        │   │RabbitMQ │   │
   │        │   │(events) │   │
   │        │   └────┬────┘   │
   │        │        │        │
   ▼        ▼        ▼        ▼
┌──────────────────────────────────────────────────────────┐
│                    Data Layer                             │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│  │Postgres│  │Postgres│  │Postgres│  │Postgres│        │
│  │market  │  │users   │  │orders  │  │payments│        │
│  └────────┘  └────────┘  └────────┘  └────────┘        │
│                       ┌────────┐                        │
│                       │ Redis  │                        │
│                       │(cache) │                        │
│                       └────────┘                        │
└──────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                Background Workers                         │
│  ┌───────────────────┐  ┌───────────────────┐          │
│  │ Celery Worker     │  │ Celery Beat       │          │
│  │ (currency refresh,│  │ (scheduler)       │          │
│  │  order processing)│  │                    │          │
│  └───────────────────┘  └───────────────────┘          │
│  ┌───────────────────┐  ┌───────────────────┐          │
│  │ AI Simulator      │  │ Order Expiry      │          │
│  │ (virtual users)   │  │ (TTL checker)     │          │
│  └───────────────────┘  └───────────────────┘          │
└──────────────────────────────────────────────────────────┘
```

---

## Infrastructure

### Orchestration (Kubernetes)

Each microservice is a separate `Deployment` with `HorizontalPodAutoscaler` for CPU/memory-based scaling. Services communicate via DNS (`market-service.namespace.svc.cluster.local`).

```
infra/k8s/
├── namespaces/
│   └── empire-market.yaml
├── market/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── configmap.yaml
├── user/
│   └── (same structure)
├── order/
│   └── (same structure)
├── payment/
│   └── (same structure)
├── redis/
│   ├── statefulset.yaml
│   └── service.yaml
├── rabbitmq/
│   ├── statefulset.yaml
│   └── service.yaml
├── postgres/
│   └── statefulset.yaml (per service or shared cluster)
├── ingress/
│   └── nginx-ingress.yaml
└── monitoring/
    ├── prometheus-deployment.yaml
    └── grafana-deployment.yaml
```

### Service Mesh (future)
- Istio or Linkerd for traffic splitting, retries, circuit breakers, mTLS
- Jaeger for distributed tracing across all services

### Message Broker (RabbitMQ)
- Event-driven communication between Order, Payment, and Notification services
- Exchange types: `topic` for routing by domain, `direct` for command-style
- Dead-letter queues for failed message handling
- At-least-once delivery with idempotency keys on the consumer side

### Caching (Redis)
- Currency rates (refreshed hourly via Celery Beat)
- User session data (8h TTL)
- Product catalog (invalidated on write)
- Rate limiting counters (sliding window)

### Monitoring & Observability
- **Metrics:** Prometheus scraping `/metrics` on every service
- **Dashboards:** Grafana (RPS, latency p50/p95/p99, error rate, queue depth, connection pool usage)
- **Logging:** Structured JSON logs (stdout), collected via Fluentd → Elasticsearch (future)
- **Tracing:** OpenTelemetry instrumented in FastAPI middleware → Jaeger

### CI/CD (planned)
- GitHub Actions: lint → test → build → push to registry
- ArgoCD for GitOps-style deployment to K8s
- Canary deployments with traffic splitting

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (Python 3.12+), async |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Frontend | React 19, Vite 6, React Router 7 |
| Message Broker | RabbitMQ |
| Task Queue | Celery + Redis (broker) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Reverse Proxy | Nginx |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (minikube / kind / cloud) |
| Monitoring | Prometheus + Grafana |
| External APIs | CurrencyFreaks, MaxMind GeoIP2, ipify.org |

---

## Data Flow

### Product Browse (with currency conversion)
```
User → GET /market/products
     → Nginx → Market Service
     → Extract user IP (Cloudflare / X-Forwarded-For)
     → Lookup country via GeoIP2
     → Get currency code from Redis (country_currency_code hash)
     → Get FX rate from Redis (currencies hash, refreshed by Celery)
     → Convert price: price * rate, round to 1 decimal
     → Return products with localized prices
```

### Order Placement
```
User → POST /orders
     → Auth check (JWT middleware)
     → Validate inventory (Market Service via HTTP/gRPC)
     → Publish "order.created" to RabbitMQ
     → Payment Service consumes event
     → Payment processed (mock gateway)
     → Publish "payment.completed" to RabbitMQ
     → Order Service consumes, updates status → "confirmed"
     → Celery task scheduled: auto-expire if not picked up in 24h
```

### AI Load Testing
```
AI Simulator → Spawns N virtual users
             → Each user: register → login → browse → order → pay
             → Random think times (100-3000ms)
             → Random product selection
             → Metrics collected: success rate, latency, error distribution
             → Reports: max concurrent users before p99 exceeds 500ms
```

---

## Services

| Service | Port | DB | Description |
|---------|------|----|-------------|
| Market | :8000 | market_db | Products, inventory, geo-currency conversion |
| User | :8001 | user_db | Registration, auth (JWT), roles (admin/seller/consumer) |
| Order | :8002 | order_db | Order lifecycle: create → confirm → ship → deliver |
| Payment | :8003 | payment_db | Mock payment processing, refunds, idempotency |
| Redis | :6379 | — | Cache (FX rates, sessions, rate limits) |
| RabbitMQ | :5672 | — | Event bus (order.paid, payment.failed, etc.) |
| Postgres | :5432 | — | Per-service databases or schema-per-service |

---

## Endpoints

### Market Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /market/products | No | List all products (localized price) |
| GET | /market/product | No | Get product by ID (localized price) |
| POST | /market/product | Admin | Create product |
| PUT | /market/product/{id} | Admin | Update product |
| DELETE | /market/product/{id} | Admin | Soft-delete product |

### User Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /user/register | No | Register new user |
| POST | /user/login | No | Get JWT token pair |
| POST | /user/refresh | Refresh | Refresh access token |
| GET | /user/me | JWT | Get current user profile |

### Order Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /orders | JWT | Create order (→ RabbitMQ) |
| GET | /orders | JWT | List user orders |
| GET | /orders/{id} | JWT | Order details + status |
| POST | /orders/{id}/cancel | JWT | Cancel order |

### Payment Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /payments | JWT | Process payment for order |
| GET | /payments/{order_id} | JWT | Payment status |
| POST | /payments/{order_id}/refund | Admin | Issue refund |

---

## Development

### Prerequisites
- Python 3.12+, Node.js 22+, Docker, kubectl, kind or minikube

### Local (Docker Compose)
```bash
docker compose up --build
```
- Frontend: http://localhost
- Market API docs: http://localhost:8000/docs
- User API docs: http://localhost:8001/docs

### Local (without Docker)
```bash
# Backend (each in separate terminal)
uv venv && source .venv/bin/activate && uv sync
uvicorn app.main:app --reload --port 8000
uvicorn user_app.main:app --reload --port 8001

# Celery
celery -A celery_app.currency worker --loglevel=INFO
celery -A celery_app.currency beat --loglevel=INFO

# Frontend
cd frontend && npm install && npm run dev
```

### Kubernetes (kind/minikube)
```bash
kind create cluster
kubectl apply -f infra/k8s/namespaces/
kubectl apply -f infra/k8s/postgres/
kubectl apply -f infra/k8s/redis/
kubectl apply -f infra/k8s/rabbitmq/
kubectl apply -f infra/k8s/market/
kubectl apply -f infra/k8s/user/
# ... etc
kubectl apply -f infra/k8s/ingress/
```

---

## Testing

```bash
pytest -v
```

All tests use mocked DB / Redis — no infrastructure required.

### Load Testing (future)
```bash
# AI simulator: spawns 1000 virtual users
python ai_simulator/main.py --users 1000 --rate 50/s
```
Metrics pushed to Prometheus, visualized in Grafana.

---

## Project Structure

```
empire-market/
├── app/                  # Market service
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers.py
│   ├── databases.py
│   ├── middleware/
│   │   └── ip_address.py
│   ├── alembic/
│   └── Dockerfile
├── user_app/             # User service
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers.py
│   ├── databases.py
│   ├── enums.py
│   └── Dockerfile
├── order_service/        # Order service (planned)
├── payment_service/      # Payment service (planned)
├── celery_app/
│   └── currency.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── pages/
│   └── Dockerfile
├── ai_simulator/         # Load testing suite (planned)
├── infra/
│   └── k8s/              # Kubernetes manifests (planned)
├── tests/
│   ├── conftest.py
│   ├── test_app.py
│   └── test_user_app.py
├── docker-compose.yml
├── ngnix.conf
└── pyproject.toml
```
