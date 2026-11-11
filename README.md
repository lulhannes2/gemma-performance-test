# Gemma Performance Testing & Inference
## Local AI Project - CJIB Innovatielab

Production-grade performance testing and on-demand inference for Gemma 2 LLMs on DGX A100 hardware.

---

## 📋 Project Status

- **US-001**: Gemma 2 26B Model Deployment (🔄 In Progress)
- **US-002**: Performance Testing (⏳ Queued)
- **US-003**: Gemma 2 31B Model Deployment (⏳ Queued)
- **US-004**: Performance Testing 31B (⏳ Queued)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12
- Docker & Docker Compose (with GPU support)
- NVIDIA GPU (A100 recommended)
- 120GB+ RAM
- ~50GB disk (for models)

### Setup Environment

```bash
# Clone repo
git clone https://github.com/lulhannes2/gemma-performance-test.git
cd gemma-performance-test

# Create Python environment
chmod +x setup.sh
./setup.sh

# Activate venv
source .venv/bin/activate
```

### Run Inference Server

```bash
# Build and start container
docker-compose build
docker-compose up gemma-26b

# In another terminal, test
python test_client.py --model 26b
```

---

## 📁 Project Structure

```
.
├── userstories.md                          # User stories & requirements
├── DEMO_PRESENTATION.md                    # Demo slides & findings
├── HARDWARE_IMPACT_ANALYSIS.md             # Hardware specs & tradeoffs
├── README.md                               # This file
├── .gitignore                              # Git ignore rules
│
├── setup.sh                                # Environment setup script
├── pyproject.toml                          # Python dependencies
│
├── inference_server.py                     # FastAPI server (core)
├── Dockerfile                              # Container definition
├── docker-compose.yml                      # Multi-model orchestration
├── test_client.py                          # HTTP client for testing
├── README_INFERENCE.md                     # Inference server docs
│
├── monitor_gpu.py                          # GPU monitoring daemon
├── check_gpu_clocks.py                     # Clock speed monitor
├── gpu_max_specs.sh                        # GPU specs query
├── gpu_monitor_simple.sh                   # Simple nvidia-smi wrapper
├── diagnose_pcie.sh                        # PCIe troubleshooting
│
└── logs/                                   # Request logs (auto-generated)
    ├── requests_*.jsonl                    # Request/response logs
    └── inference_server.log                # Server logs
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Model
MODEL_NAME=google/gemma-2-26b              # Model to load
GPU_MEMORY_UTILIZATION=0.95                # GPU memory %
MAX_MODEL_LEN=32768                        # Context length

# Server
PORT=8000                                  # Server port
HOST=0.0.0.0                              # Bind address

# Docker
shm_size: 100gb                           # Shared memory
mem_limit: 120gb                          # Container memory
```

See `docker-compose.yml` for full config.

---

## 📊 API Endpoints

### Generate Text
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain AI in simple terms",
    "max_tokens": 256,
    "temperature": 0.7
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Server Stats
```bash
curl http://localhost:8000/stats
```

See `README_INFERENCE.md` for full API documentation.

---

## 🧪 Testing

### Quick Test
```bash
python test_client.py --model 26b
```

### Load Test (TODO)
```bash
python load_test.py --requests 50 --model 26b
```

### View Logs
```bash
docker-compose logs -f gemma-26b
tail -f logs/requests_*.jsonl
```

---

## 🖥️ Monitoring

### GPU Stats
```bash
# Real-time GPU monitoring
nvidia-smi dmon -s pucvmet

# Or via Python
python monitor_gpu.py

# Clock speeds
python check_gpu_clocks.py
```

### PCIe Bottleneck Status
```bash
# Check if GPU has PCIe bottleneck (critical for performance)
/usr/bin/nvidia-smi -i 0 -q | grep -A 2 "Link Width"

# Expected output:
# Link Width
# Max                                    : 16x
# Current                                : 16x ✅ (optimal) or 1x ❌ (bottleneck)
```

### Container Stats
```bash
docker stats gemma-26b-inference
```

---

## 📈 Performance Benchmarking

See `userstories.md` for full benchmarking methodology.

```bash
# Run performance tests
python test_performance.py --model gemma-2-26b

# Results logged to logs/
ls -lh logs/gemma_2_26b_*.jsonl
```

---

## 🐛 Known Issues

### PCIe Bottleneck (CRITICAL)
- **Status**: Investigating with hardware team
- **Impact**: ~93% bandwidth loss (1x vs 16x)
- **Workaround**: None (requires BIOS/physical intervention)
- **See**: `HARDWARE_IMPACT_ANALYSIS.md` for details

### Temperature Management
- **Status**: ✅ Nominal (35°C idle, 60-75°C under load)
- **Headroom**: 25°C before throttling

---

## 🚀 Next Steps

1. **Week 1 (This Week)**
   - [x] Environment setup (Python, Docker)
   - [x] Inference server development
   - [ ] Deploy Gemma 2 26B container
   - [ ] Baseline performance test

2. **Week 2**
   - [ ] Gemma 2 31B deployment
   - [ ] Comparative performance analysis
   - [ ] PCIe investigation (with hardware team)

3. **Week 3+**
   - [ ] Multi-node clustering setup
   - [ ] Distributed performance tests
   - [ ] Production deployment guide

---

## 📚 Documentation

- `DEMO_PRESENTATION.md` - Presentation slides for stakeholders
- `HARDWARE_IMPACT_ANALYSIS.md` - Hardware specs & performance tradeoffs
- `README_INFERENCE.md` - Inference server API documentation
- `userstories.md` - Detailed user stories & acceptance criteria

---

## 🔒 Security Notes

- Models cached locally: `./huggingface_cache/`
- Logs contain prompts & responses: protect `./logs/`
- API has no auth (deployment only - add auth for production)
- GPU access requires `nvidia-docker` runtime

---

## 📞 Support

Issues or questions? Check:
1. Docker logs: `docker-compose logs gemma-26b`
2. GPU status: `nvidia-smi`
3. Network: `curl http://localhost:8000/health`

---

## 📜 License

Internal project - CJIB Innovatielab

---

**Last Updated**: Nov 10, 2026
**Project Lead**: lulhannes2@github
**Host**: dgx43019 (Tailscale)
