# Mijn user stories local AI project CJIB - Innovatielab
## Environment Setup Requirements
- **Python**: 3.12
- **Host**: dgx43019 (DGX A100, NVIDIA GPU)
- **Inference Framework**: vLLM (for optimal performance testing)
- **Model Source**: HuggingFace
- **Logging**: JSON format to `./logs/` directory (root of project)
- **Data Transfer**: SCP/rsync to pull logs to laptop after testing

## US-001
**Titel**:
Als ai-engineer wil ik Gemma 4 26B op dgx43019 installeren en valideren.
**Beschrijving**:
- Download Gemma 2 26B model van HuggingFace
- Setup Python 3.12 venv met vLLM
- Verify model loading en basic inference
- Test met simple prompt (< 500 tokens context)
**DoD**
- [x] Model beschikbaar in HuggingFace cache op dgx43019
- [x] vLLM server draait zonder errors
- [x] Simpele inference test geslaagd (prompt + response gelogd in JSON)
- [x] GPU memory usage gemonitord
**Acceptance Criteria**:
- Model loaded in < 2 minuten
- First token latency < 5 seconds
- Response completes successfully
---

## US-002
**Titel**:
Als ai-engineer wil ik Gemma 2 26B performance-testen met groeiende context grootten.
**Beschrijving**:
- Start context size: 8K tokens
- Incrementeel prompt vergroten tot failure/max
- Test variabelen: TPS, latency, memory usage, throughput
- Log alles in JSON per test run
- Bepaal point of failure (waar model crashes of onacceptabele delays)
**Context Size Stappen**:
- 8K (baseline)
- 16K
- 24K
- 32K (or max supported)
**Metrics per test** (JSON logged):
```json
{
  "model": "gemma-2-26b",
  "timestamp": "ISO8601",
  "context_size": 8192,
  "prompt_tokens": 1234,
  "response_tokens": 456,
  "first_token_latency_ms": 1200,
  "total_latency_ms": 5600,
  "tokens_per_second": 81.4,
  "gpu_memory_used_gb": 18.5,
  "gpu_memory_peak_gb": 19.2,
  "status": "success" // or "timeout", "oom", "error"
}
```

**DoD**
- [x] Performance test script geautomatiseerd (incremental context growth)
- [x] Minimaal 3 runs per context size
- [x] Failure point gedocumenteerd (waar model faalt/timeout)
- [x] Alle resultaten in JSON logs in `./logs/`
- [x] Report gegenereerd met samenvatting per context size
- [x] Klaar voor clustering tests (volgende week)
**Acceptance Criteria**:
- Logs compleet en parseable
- Min 1 context size waar model faalt
- Performance degradation trend zichtbaar
- Wachtijden mapped tot usability grens (bijv. 30s = too slow)
---

## US-003
**Titel**:

Als ai-engineer wil ik Gemma 2 31B op dgx43019 installeren en valideren.
**Beschrijving**:
- Download Gemma 2 31B model van HuggingFace
- Reuse venv van US-001 (of aparte)
- Verify model loading en basic inference
- Test met simple prompt (< 500 tokens context)
**DoD**
- [x] Model beschikbaar in HuggingFace cache op dgx43019
- [x] vLLM server draait zonder errors
- [x] Simpele inference test geslaagd (prompt + response gelogd in JSON)
- [x] GPU memory usage gemonitord
**Acceptance Criteria**:
- Model loaded in < 3 minuten (groter model)
- First token latency < 10 seconds
- Response completes successfully
---

## US-004
**Titel**:
Als ai-engineer wil ik Gemma 2 31B performance-testen met groeiende context grootten.
**Beschrijving**:
- Identiek aan US-002, maar voor Gemma 2 31B
- Start context size: 8K tokens
- Incrementeel prompt vergroten tot failure/max
- Test variabelen: TPS, latency, memory usage, throughput
- Log alles in JSON per test run
- Bepaal point of failure
**Context Size Stappen**:
- 8K (baseline)
- 16K
- 24K
- 32K (or max supported)
**Metrics**: Identiek aan US-002 (zie hierboven)
**DoD**
- [x] Performance test script geautomatiseerd (incremental context growth)
- [x] Minimaal 3 runs per context size
- [x] Failure point gedocumenteerd
- [x] Alle resultaten in JSON logs in `./logs/`
- [x] Report gegenereerd met samenvatting per context size
- [x] Vergelijking 26B vs 31B performance (optioneel)
- [x] Klaar voor clustering tests (volgende week)
**Acceptance Criteria**:
- Logs compleet en parseable
- Min 1 context size waar model faalt
- Performance degradation trend zichtbaar
- 31B vs 26B tradeoffs duidelijk (groter model = meer memory, maar beter quality)
---
## Technical Stack
```bash
# venv setup
python3.12 -m venv /path/to/venv
source /path/to/venv/bin/activate
# Dependencies
pip install vllm transformers pydantic torch
# Model download (HuggingFace CLI)
huggingface-cli download google/gemma-2-26b
huggingface-cli download google/gemma-2-31b
```
## Log Management
- **Location**: `./logs/` on dgx43019
- **Format**: JSON (one object per line)
- **Transfer to laptop**: 
  ```bash
  scp -r dgx43019:/path/to/logs /local/laptop/path
  # or
  tailscale file cp dgx43019:/path/to/logs /local/path
  ```
## Timeline
- **Today (Week 1)**: US-001, US-002 (26B model + testing)
- **Tomorrow (Week 1)**: US-003, US-004 (31B model + testing)
- **Next Week**: Cluster setup + rerun tests across 4x DGX machines