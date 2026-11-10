# Gemma Inference Server (On-Demand, Request-Based)

## Overview

This is a **containerized, request-based inference API** for Gemma 2 models. Key features:

✅ **On-Demand Inference** - Model loads only when requests arrive (no GPU idle waste)
✅ **FastAPI REST Interface** - Easy HTTP API for requests  
✅ **vLLM Backend** - Ultra-fast inference engine
✅ **Automatic Logging** - All requests logged to JSON
✅ **Reusable Pipeline** - Works with any HuggingFace model
✅ **Docker Containerized** - Portable, reproducible setup
✅ **Health Checks** - Built-in monitoring

---

## Quick Start

### 1. Build the Container

```bash
# Build image for both models
docker-compose build
```

### 2. Run Gemma 2 26B Server

```bash
# Start 26B model on port 8000
docker-compose up gemma-26b
```

**Output:**
```
gemma-26b-inference  | INFO:     Application startup complete [uvicorn]
gemma-26b-inference  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

Server is ready! ✅

### 3. Send a Request

In another terminal:

```bash
# Test with CLI
python test_client.py --model 26b

# Or manually
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain machine learning in simple terms.",
    "max_tokens": 256,
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "prompt": "Explain machine learning...",
  "generated_text": "Machine learning is a type of artificial intelligence...",
  "prompt_tokens": 8,
  "generated_tokens": 145,
  "latency_ms": 3200,
  "tokens_per_second": 45.3,
  "model": "google/gemma-2-26b",
  "timestamp": "2026-11-10T15:30:45.123456"
}
```

---

## Architecture

### On-Demand Loading

```
Request arrives
    ↓
[Is model loaded?]
    ├─ YES → Generate immediately
    └─ NO → Load model → Generate
    ↓
Return response
↓
[Idle] → Model stays in GPU memory for next request
```

**Benefits:**
- ✅ No wasted GPU compute (model not running when idle)
- ✅ Minimal startup overhead for next request
- ✅ Scales naturally with traffic

---

## API Endpoints

### `/generate` (POST)
**Generate text completion**

Request:
```json
{
  "prompt": "Your text here",
  "max_tokens": 256,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 50
}
```

Response:
```json
{
  "prompt": "...",
  "generated_text": "...",
  "prompt_tokens": 10,
  "generated_tokens": 150,
  "latency_ms": 3500,
  "tokens_per_second": 42.8,
  "model": "google/gemma-2-26b",
  "timestamp": "2026-11-10T15:30:45Z"
}
```

### `/health` (GET)
**Check if server is alive** (doesn't load model)

Response:
```json
{
  "status": "ok",
  "model": "google/gemma-2-26b",
  "gpu_available": true,
  "timestamp": "2026-11-10T15:30:45Z"
}
```

### `/ready` (GET)
**Check if model is loaded & ready** (triggers model load if needed)

### `/stats` (GET)
**Get server statistics**

Response:
```json
{
  "total_requests": 42,
  "model": "google/gemma-2-26b",
  "gpu_memory_utilization_target": 0.9,
  "max_model_length": 32768,
  "model_loaded": true,
  "timestamp": "2026-11-10T15:30:45Z"
}
```

### `/unload` (POST)
**Manually unload model from GPU** (frees memory)

---

## Configuration

Environment variables (in `docker-compose.yml`):

```yaml
MODEL_NAME=google/gemma-2-26b           # Which model to load
GPU_MEMORY_UTILIZATION=0.9              # GPU memory % to use
MAX_MODEL_LEN=32768                     # Max context length
PORT=8000                               # Server port
LOG_DIR=/app/logs                       # Where to save logs
```

---

## Testing & Benchmarking

### Test Single Request

```bash
python test_client.py --model 26b
```

### Test Multiple Requests (Load Test)

```bash
# Script to send multiple requests
python load_test.py --requests 10 --model 26b
```

### View Logs

```bash
# Real-time logs
docker-compose logs -f gemma-26b

# Saved request logs
tail -f logs/requests_*.jsonl
```

---

## Running 31B Model

The same container supports Gemma 2 31B:

```bash
# Start 31B server (port 8001)
docker-compose up --profile 31b gemma-31b

# Test it
python test_client.py --model 31b --url http://localhost:8001
```

---

## Memory & Performance Tuning

### If Running Out of Memory:

```yaml
# In docker-compose.yml
GPU_MEMORY_UTILIZATION=0.85  # Reduce from 0.9
```

### If Want Faster Inference:

```yaml
GPU_MEMORY_UTILIZATION=0.95  # Increase (but risk OOM)
```

### Check GPU Usage:

```bash
# From host (outside container)
nvidia-smi dmon -s pucvmet
```

---

## Reusability for Other Models

To use a different model, just update `docker-compose.yml`:

```yaml
services:
  my-model:
    environment:
      - MODEL_NAME=meta-llama/Llama-2-7b-hf  # Any HF model!
      - PORT=8002
```

Or at runtime:

```bash
docker run \
  --gpus all \
  -e MODEL_NAME=meta-llama/Llama-2-7b-hf \
  gemma-inference:latest
```

**Fully reusable pipeline!** ✅

---

## Troubleshooting

### Server won't start
```bash
# Check logs
docker-compose logs gemma-26b

# Common: Out of memory
# → Reduce GPU_MEMORY_UTILIZATION
```

### Connection refused
```bash
# Make sure container is running
docker-compose ps

# Start if not running
docker-compose up gemma-26b
```

### Slow responses
```bash
# Check GPU stats
nvidia-smi dmon

# Check if other processes using GPU
nvidia-smi
```

---

## Next Steps

1. **Deploy** - Running inference server on dgx43019
2. **Test** - Send sample requests and verify latency
3. **Scale** - Add load testing for context size escalation
4. **Integrate** - Connect to performance testing pipeline (US-002)

---

## Files

```
.
├── inference_server.py        # FastAPI server code
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Multi-model orchestration
├── test_client.py             # HTTP client for testing
├── README_INFERENCE.md        # This file
└── logs/                      # Request logs (auto-created)
    ├── requests_20261110.jsonl
    └── inference_server.log
```

---

**Ready to deploy!** 🚀
