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

## Live Demo

🚀 **https://styleforge-blush.vercel.app**

## Image Generator Implementations

### StubGenerator (Default - Free)
Returns original image with style-specific color grading and effects. Great for testing the UI/UX without AI costs.

### RealGenerator (Replicate - Paid)
Uses [Replicate](https://replicate.com) API with Stable Diffusion XL for actual AI-powered clothing changes.

**Cost:** ~$0.01-0.05 per image

## Setting Up AI Generation (Replicate)

1. Sign up at **https://replicate.com** (free account)
2. Go to **https://replicate.com/account/api-tokens**
3. Create a new API token
4. Add credits at **https://replicate.com/account/billing** (minimum ~$5)
5. Set environment variables:
   ```
   REPLICATE_API_TOKEN=r8_your_token_here
   IMAGE_GENERATOR=real
   ```

### AI Pricing Comparison

| Service | Cost/Image | Quality | Face Preservation |
|---------|-----------|---------|-------------------|
| **Replicate (SDXL)** | ~$0.01-0.05 | ⭐⭐⭐⭐ | Medium |
| **Replicate (IP-Adapter)** | ~$0.03-0.08 | ⭐⭐⭐⭐⭐ | High |
| **fal.ai** | ~$0.01-0.03 | ⭐⭐⭐⭐ | Medium |
| **OpenAI DALL-E 3** | ~$0.04-0.08 | ⭐⭐⭐⭐ | Low |

To switch generators, set `IMAGE_GENERATOR=stub` or `IMAGE_GENERATOR=real` in your environment.

## Deployment

### Free Hosting Stack

| Service | Component | Free Tier |
|---------|-----------|-----------|
| **Vercel** | Frontend (Next.js) | Unlimited |
| **Render** | Backend (FastAPI) | 750 hrs/month |
| **Upstash** | Redis | 10k commands/day |

### Deploy to Production

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create styleforge --public --source=. --push
   ```

2. **Set up Upstash Redis**
   - Go to https://upstash.com
   - Create a database
   - Copy the Redis URL

3. **Deploy Backend to Render**
   - Go to https://render.com
   - New → Web Service → Public Git Repository
   - Repo: `https://github.com/YOUR_USERNAME/styleforge`
   - Root Directory: `apps/api`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables (see below)

4. **Deploy Frontend to Vercel**
   - Go to https://vercel.com
   - Import your GitHub repo
   - Root Directory: `apps/web`
   - Add: `NEXT_PUBLIC_API_URL=https://your-api.onrender.com`

### Production Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Upstash Redis URL | `rediss://default:xxx@xxx.upstash.io:6379` |
| `IMAGE_GENERATOR` | `stub` or `real` | `real` |
| `REPLICATE_API_TOKEN` | Replicate API key | `r8_xxx` |
| `CORS_ORIGINS` | Frontend URL | `https://your-app.vercel.app` |
| `UPLOAD_DIR` | Upload path | `/tmp/uploads` |
| `OUTPUT_DIR` | Output path | `/tmp/outputs` |
| `METADATA_DIR` | Metadata path | `/tmp/metadata` |
| `PROCESS_INLINE` | Skip worker | `true` |

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

