# StyleForge - AI Style Transfer MVP

Transform your photos with different fashion style presets while preserving your identity.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js Web   │────▶│   FastAPI API   │────▶│   Redis Queue   │
│   (Port 3000)   │     │   (Port 8000)   │     │   (Port 6379)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  Local Storage  │     │   RQ Worker     │
                        │  /data/uploads  │     │  (Background)   │
                        │  /data/outputs  │     └─────────────────┘
                        └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Run with Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd /path/to/styleforge

# Copy environment files
cp .env.example .env
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env

# Note: App renamed from StyleForge to StyleForge

# Start all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend (FastAPI)

```bash
cd apps/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Start Redis (required for job queue)
docker run -d -p 6379:6379 redis:alpine

# Run API server
uvicorn app.main:app --reload --port 8000

# In another terminal, run the worker
rq worker styleforge --with-scheduler
```

#### Frontend (Next.js)

```bash
cd apps/web

# Install dependencies
npm install

# Run development server
npm run dev
```

## Project Structure

```
.
├── apps/
│   ├── api/                    # Python FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py         # FastAPI app entry
│   │   │   ├── config.py       # Configuration
│   │   │   ├── models.py       # Pydantic models
│   │   │   ├── routes/         # API endpoints
│   │   │   ├── services/       # Business logic
│   │   │   ├── generators/     # Image generation
│   │   │   ├── workers/        # Background tasks
│   │   │   └── middleware/     # Logging, rate limiting
│   │   ├── tests/              # Unit tests
│   │   ├── data/               # Storage (gitignored)
│   │   │   ├── uploads/
│   │   │   ├── outputs/
│   │   │   └── metadata/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web/                    # Next.js frontend
│       ├── app/                # App Router pages
│       ├── components/         # React components
│       ├── lib/                # Utilities
│       ├── package.json
│       └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/styles` | List available style presets |
| POST | `/api/jobs` | Create new transformation job |
| GET | `/api/jobs/{job_id}` | Get job status and result |
| GET | `/health` | Health check |
| GET | `/metrics` | Basic metrics |

### Create Job Request

```json
POST /api/jobs
Content-Type: multipart/form-data

{
  "image": <file>,
  "style_id": "classic-tuxedo"
}
```

### Job Response

```json
{
  "job_id": "uuid-here",
  "status": "completed",
  "progress": 100,
  "result_url": "/outputs/uuid-result.png",
  "error": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Style Presets

| ID | Name | Description |
|----|------|-------------|
| `classic-tuxedo` | Classic Tuxedo | Elegant spy archetype in formal wear |
| `streetwear` | Modern Streetwear | Urban fashion with hoodies and sneakers |
| `techwear` | Techwear | Functional futuristic clothing |
| `old-money` | Old Money | Refined preppy aesthetic |
| `minimalist` | Minimalist | Clean, simple, monochrome looks |
| `cyberpunk` | Cyberpunk | Neon-accented futuristic fashion |
| `crypto-bro` | Crypto Bro | Tech founder vibes with hoodies and Patagonia vests |

## Adding New Styles

1. Edit `apps/api/app/services/style_registry.py`
2. Add new `StylePreset` entry with:
   - Unique `id` (kebab-case)
   - Display `name`
   - `description` for UI
   - `prompt` template for image generation
   - `thumbnail` path (optional)

Example:
```python
StylePreset(
    id="bohemian",
    name="Bohemian",
    description="Free-spirited, artistic, layered clothing",
    prompt="wearing bohemian style clothing with flowing fabrics, artistic patterns, layered accessories, natural earthy tones",
    thumbnail="/thumbnails/bohemian.jpg"
)
```

## Image Generator Implementations

### StubGenerator (Default)
Returns original image with style watermark. Use for local testing without AI services.

### RealGenerator (TODO)
Skeleton implementation with clear function boundaries for integrating actual AI image generation:
- Face detection and preservation
- Style transfer via diffusion models
- Background preservation

To switch generators, set `IMAGE_GENERATOR=real` in `.env`.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `UPLOAD_DIR` | Upload storage path | `./data/uploads` |
| `OUTPUT_DIR` | Output storage path | `./data/outputs` |
| `MAX_FILE_SIZE_MB` | Max upload size | `10` |
| `RATE_LIMIT_PER_MINUTE` | Requests per IP | `30` |
| `IMAGE_GENERATOR` | Generator to use | `stub` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000` |

## Security Features

- ✅ File type validation (jpg, png, webp only)
- ✅ File size limits (10MB default)
- ✅ Rate limiting per IP
- ✅ CORS configuration
- ✅ Request ID tracking
- ✅ Structured logging

## Testing

```bash
# Backend tests
cd apps/api
pytest tests/ -v

# Frontend tests
cd apps/web
npm test
```

## License

MIT

