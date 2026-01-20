# Support-Led Ordering System - POC

A FastAPI-based backend for the Customer Support system integrated with Freshchat.

## Architecture

- **FastAPI** - API Gateway and REST endpoints
- **PostgreSQL** - Persistent storage for incidences, timeline, analytics
- **Redis** - Caching for user context and sessions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Copy the example env file
cp .env.example .env
# Edit .env with your credentials
```

### 3. Start with Docker (Recommended)

```bash
docker-compose up -d
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Access API Docs

Open http://localhost:8000/docs for Swagger UI

## Project Structure

```
poc/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # PostgreSQL + Redis connections
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── routers/             # API endpoints
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhooks/freshchat` | POST | Freshchat webhook handler |
| `/api/v1/context/update` | POST | Update user context |
| `/api/v1/channel/route` | POST | Get allowed channels |
| `/api/v1/friction/detect` | POST | Calculate friction score |
| `/api/v1/incidences` | GET/POST | Incidence CRUD |
| `/api/v1/analytics/kpis` | GET | Dashboard KPIs |

## Channel Routing Rules

| Order Value | Allowed Channels |
|-------------|------------------|
| < ₹5,000 | None (self-serve) |
| ₹5,000 - ₹25,000 | Chat only |
| > ₹25,000 | Chat + Call |
