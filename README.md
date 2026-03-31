# EpidBot-OpenMAIC Bridge

> **AI-Powered Epidemiological Education Platform**
>
> A bridge service that generates epidemiological training content using real SINAN surveillance data and OpenMAIC's multi-agent classroom platform.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

This project creates a bridge between two powerful platforms:

- **[EpidBot](https://github.com/Deelearn-PeD/EpiDBot)** - AI assistant for epidemiology with access to disease surveillance data (SINAN, WHO, etc.)
- **[OpenMAIC](https://github.com/THU-MAIC/OpenMAIC)** - Multi-agent interactive classroom platform

The bridge fetches real epidemiological data, generates rich training content, and creates interactive classrooms via OpenMAIC's API.

---

## Features

| Feature | Status |
|---------|--------|
| Fetch dengue data from SINAN via PySUS | Done |
| Generate training requirement strings with real statistics | Done |
| Submit classroom generation jobs to OpenMAIC | Done |
| Poll job status and retrieve classroom URLs | Done |
| REST API with FastAPI | Done |
| Multi-disease support (Zika, Chikungunya, etc.) | Planned |
| Interactive outbreak simulations | Planned |
| Export to PPTX/PDF | Planned |

---

## Prerequisites

1. **Python 3.12+**
2. **uv** package manager ([install guide](https://docs.astral.sh/uv/))
3. **OpenMAIC** running at `localhost:3000` (or configure `OPENMAIC_URL`)
4. **EpidBot** API key (configure `EPIDBOT_API_KEY`)

---

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/deeplearn/EpidBot-OpenMAIC.git
cd EpidBot-OpenMAIC

# Install dependencies with uv
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed:
```bash
# OpenMAIC Configuration
OPENMAIC_URL=http://localhost:3000

# EpidBot Configuration
EPIDBOT_URL=https://api.epidbot.kwar-ai.com.br
EPIDBOT_API_KEY=your-epidbot-api-key

# PySUS Data Cache Directory
PYSUS_DATA_PATH=~/pysus

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 3. Start the Bridge Service

```bash
# Using the configured script
uv run serve

# Or directly with uvicorn
uv run uvicorn src.main:app --reload --port 8000
```

### 4. Verify the Service

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "epidbot-openmaic-bridge",
  "openmaic_connected": true,
  "epidbot_connected": true
}
```

---

## API Endpoints

### Health Check

```bash
GET /health
```

Returns service status and OpenMAIC connectivity.

---

### Generate Dengue Training

```bash
POST /api/generate-dengue-training
```

Generate a dengue training classroom with real SINAN data.

**Request Body:**
```json
{
  "region": "São Paulo",
  "year": 2024,
  "state": "SP",
  "language": "pt-BR",
  "target_audience": "agentes de saúde",
  "num_slides": 8,
  "num_quizzes": 3
}
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "processing",
  "data_summary": {
    "total_cases": 12345,
    "deaths": 15,
    "hospitalizations": 234,
    "fatality_rate": 0.12
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/generate-dengue-training \
  -H "Content-Type: application/json" \
  -d '{"region": "São Paulo", "year": 2024, "state": "SP"}'
```

---

### Poll Job Status

```bash
GET /api/job/{job_id}
```

Check the status of a classroom generation job.

**Response:**
```json
{
  "job_id": "abc123",
  "status": "completed",
  "progress": 100,
  "classroom_url": "http://localhost:3000/classroom/xyz",
  "classroom_id": "xyz"
}
```

**Status Values:**
- `queued` - Job is waiting to start
- `processing` - Job is running
- `completed` - Job finished successfully
- `failed` - Job encountered an error

---

### Get Classroom

```bash
GET /api/classroom/{classroom_id}
```

Retrieve the full classroom data after generation completes.

---

## EpidBot API Integration

The bridge connects to EpidBot via its REST API to leverage epidemiological AI capabilities.

### Configuration

```bash
EPIDBOT_URL=https://api.epidbot.kwar-ai.com.br
EPIDBOT_API_KEY=your-api-key
```

### EpidBot Adapter

The `EpidBotAdapter` class provides:

| Method | Description |
|--------|-------------|
| `create_session()` | Create a new chat session |
| `chat(message)` | Send a message and receive AI response |
| `health_check()` | Verify EpidBot connectivity |

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/sessions` | POST | Create chat session |
| `/api/v1/chat` | POST | Send chat message |
| `/api/v1/health` | GET | Health check |

### Authentication

All requests require the `X-API-Key` header:
```bash
curl -H "X-API-Key: your-api-key" https://api.epidbot.kwar-ai.com.br/api/v1/health
```

---

## Running the Demo

The demo script demonstrates the end-to-end flow:

```bash
# Make sure the bridge service is running first
uv run serve &

# Run the demo
uv run python scripts/demo.py
```

The demo will:
1. Check service health
2. Submit a dengue training generation request
3. Poll for completion
4. Display the classroom URL when ready

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_basic.py -v
```

---

## Project Structure

```
EpidBot-OpenMAIC/
├── pyproject.toml          # Project config (uv-compatible)
├── .env.example            # Environment template
├── .env                    # Local configuration
├── uv.lock                 # Dependency lock file
├── src/
│   ├── __init__.py
│   ├── config.py           # Pydantic settings
│   ├── main.py             # FastAPI application
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── openmaic_adapter.py   # OpenMAIC HTTP client
│   ├── generators/
│   │   ├── __init__.py
│   │   └── requirement_builder.py  # Builds requirement strings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py      # Pydantic request/response models
│   └── utils/
│       ├── __init__.py
│       └── data_fetcher.py # PySUS data fetching
├── tests/
│   ├── __init__.py
│   └── test_basic.py
├── scripts/
│   └── demo.py             # End-to-end demo
└── docs/
    ├── ARCHITECTURE.md
    ├── IMPLEMENTATION_PLAN.md
    └── USE_CASES.md
```

---

## Development

### Code Formatting

```bash
uv run ruff format src/ tests/
```

### Linting

```bash
uv run ruff check src/ tests/
```

### Type Checking

```bash
uv run mypy src/
```

---

## Architecture

```
User Request
     │
     ▼
┌─────────────────────────────────────────┐
│         EpidBot-OpenMAIC Bridge          │
│                                         │
│  1. Fetch SINAN data via PySUS          │
│  2. Summarize statistics                │
│  3. Build rich requirement string       │
│  4. Submit to OpenMAIC API              │
│                                         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│              OpenMAIC                    │
│                                         │
│  POST /api/generate-classroom          │
│  → Generates slides, quizzes, agents   │
│  → Returns classroom URL                │
└─────────────────────────────────────────┘
```

---

## Roadmap

### Phase 1 (Current - MVP)
- [x] Basic project structure
- [x] FastAPI service
- [x] OpenMAIC adapter
- [x] Dengue data fetching via PySUS
- [x] Requirement builder
- [x] Basic tests

### Phase 2 (Next)
- [ ] Multi-disease support (Zika, Chikungunya, COVID-19)
- [ ] Enhanced requirement templates
- [ ] Data visualization generation
- [ ] Error handling improvements

### Phase 3 (Future)
- [ ] Interactive outbreak simulations
- [ ] Real-time data integration
- [ ] Export to PPTX/PDF
- [ ] LMS integration (Moodle)

---

## Contributing

We welcome contributions! Priority areas:

- Multi-disease support
- Improved requirement templates
- Test coverage
- Documentation

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Acknowledgments

- [OpenMAIC](https://github.com/THU-MAIC/OpenMAIC) - Tsinghua University
- [EpidBot](https://github.com/Deelearn-PeD/EpiDBot) - Kwar-AI
- [PySUS](https://github.com/AlertaDengue/PySUS) - Alerta Dengue
