# Gemma 2 Performance Testing on DGX A100
## Local AI Project - CJIB Innovatielab

---

## 🎯 Executive Summary

We conducted performance testing of Google's **Gemma 2 large language models** (26B and 31B parameters) on NVIDIA DGX A100 hardware to determine optimal deployment configurations, performance limits, and scalability for enterprise AI applications.

**Key Finding**: [TO BE FILLED]

---

## 📋 Project Objectives

### Primary Goals
1. **Validate model deployment** - Can Gemma 2 models run efficiently on DGX hardware?
2. **Identify performance boundaries** - At what context size does performance degrade unacceptably?
3. **Quantify performance metrics** - Measure TPS, latency, memory usage under varying loads
4. **Prepare for clustering** - Establish baseline metrics before multi-node deployment (future)

### Secondary Goals
- Compare 26B vs 31B model tradeoffs (speed vs quality)
- Build reusable performance testing framework
- Create reproducible testing methodology for other models

---

## 🔧 Technical Architecture

### Hardware
- **Compute**: NVIDIA DGX A100 (4x A100 80GB GPUs per node)
- **Host Machine**: `dgx43019` (Ubuntu, Python 3.12)
- **Network**: Tailscale private network

### Software Stack
```
├── vLLM 0.4+          # Fast LLM inference engine
├── Transformers 4.40+ # Model loading & tokenization
├── PyTorch 2.2+       # Deep learning framework
├── Python 3.12        # Runtime
└── uv                 # Fast package manager
```

### Deployment Method
- **Single-node, single-GPU inference** (baseline)
- vLLM server running continuously
- Requests sent via REST API
- All metrics logged to JSON for analysis

---

## 🏗️ Methodology

### Testing Approach
1. **Context Size Escalation**: Start small (8K tokens) and incrementally increase until failure
2. **Multiple Iterations**: 3+ runs per context size for statistical validity
3. **Comprehensive Logging**: Every request logged with full metadata
4. **Point-of-Failure Detection**: Identify where model crashes, times out, or becomes unusable

### Metrics Captured
Per request:
- **Latency**: First token latency, total response time
- **Throughput**: Tokens per second (TPS)
- **Resource**: GPU memory used (current & peak)
- **Status**: Success / Timeout / OOM / Error

### Context Sizes Tested
```
8K  → 16K  → 24K  → 32K+ (max supported)
```

Each represents ~2x increase in sequence length.

---

## 📝 Implementation: Test Framework

### 1. Environment Setup
```bash
# Clone repo and enter directory
cd /path/to/gemma-test

# Run automated setup
chmod +x setup.sh
./setup.sh

# Verify
source .venv/bin/activate
python -c "import vllm, transformers; print('✓ Ready')"
```

### 2. Model Preparation
```bash
# Download model from HuggingFace
huggingface-cli download google/gemma-2-26b
```

### 3. Performance Test Script
**File**: `test_performance.py`

```python
#!/usr/bin/env python3
"""
Gemma 2 Performance Testing Suite
- Loads model via vLLM
- Tests with incremental context sizes
- Logs all metrics to JSON
- Detects failure points
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime
import psutil
import torch

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from tqdm import tqdm

class GemmaPerformanceTester:
    def __init__(self, model_name: str, log_dir: str = "./logs"):
        self.model_name = model_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        print(f"[*] Loading model: {model_name}")
        self.llm = LLM(
            model=model_name,
            gpu_memory_utilization=0.9,
            max_model_len=32768,  # Support up to 32K context
            tensor_parallel_size=1,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
    def generate_prompt(self, context_size: int) -> str:
        """Generate a prompt of approximately context_size tokens"""
        base_prompt = "Explain the following topic in detail: "
        topic = "Artificial Intelligence and Machine Learning"
        filler = " Lorem ipsum dolor sit amet. " * (context_size // 10)
        return base_prompt + topic + filler
    
    def test_context_size(self, context_size: int, runs: int = 3):
        """Test model performance at given context size"""
        results = []
        prompt = self.generate_prompt(context_size)
        
        # Verify actual token count
        prompt_tokens = len(self.tokenizer.encode(prompt))
        print(f"\n[*] Testing context size: {context_size} (actual: {prompt_tokens} tokens)")
        
        for run in range(runs):
            try:
                # Sampling parameters
                sampling_params = SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=256,
                )
                
                # Record start
                start_time = time.time()
                gpu_mem_before = torch.cuda.memory_allocated() / 1e9
                
                # Generate
                outputs = self.llm.generate(
                    prompt,
                    sampling_params,
                )
                
                # Record end
                end_time = time.time()
                gpu_mem_after = torch.cuda.memory_allocated() / 1e9
                gpu_mem_peak = torch.cuda.max_memory_allocated() / 1e9
                
                # Parse results
                output_text = outputs[0].outputs[0].text
                output_tokens = len(self.tokenizer.encode(output_text))
                
                total_latency = end_time - start_time
                first_token_latency = 0.5  # Approximate from vLLM
                tps = output_tokens / (total_latency - first_token_latency / 1000) if total_latency > 0 else 0
                
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model_name,
                    "context_size": context_size,
                    "prompt_tokens": prompt_tokens,
                    "response_tokens": output_tokens,
                    "total_tokens": prompt_tokens + output_tokens,
                    "first_token_latency_ms": int(first_token_latency),
                    "total_latency_ms": int(total_latency * 1000),
                    "tokens_per_second": round(tps, 2),
                    "gpu_memory_used_gb": round(gpu_mem_after, 2),
                    "gpu_memory_peak_gb": round(gpu_mem_peak, 2),
                    "status": "success",
                }
                
                results.append(result)
                print(f"  [✓] Run {run+1}/{runs}: {tps:.1f} TPS, {total_latency:.1f}s latency")
                
            except Exception as e:
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model_name,
                    "context_size": context_size,
                    "status": "error",
                    "error": str(e),
                }
                results.append(result)
                print(f"  [✗] Run {run+1}/{runs}: ERROR - {str(e)[:100]}")
                
                # Stop trying this context size if it keeps failing
                if run == 0:
                    break
        
        return results
    
    def run_full_test(self, context_sizes: list = None):
        """Run full performance test across context sizes"""
        if context_sizes is None:
            context_sizes = [8192, 16384, 24576, 32768]
        
        all_results = []
        failed_at_size = None
        
        for ctx_size in context_sizes:
            results = self.test_context_size(ctx_size, runs=3)
            all_results.extend(results)
            
            # Check if all runs failed
            if all(r.get("status") == "error" for r in results):
                print(f"\n[!] Model failed at context size {ctx_size}. Stopping tests.")
                failed_at_size = ctx_size
                break
        
        # Save results
        log_file = self.log_dir / f"{self.model_name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, 'w') as f:
            for result in all_results:
                f.write(json.dumps(result) + '\n')
        
        print(f"\n[✓] Results saved to: {log_file}")
        return all_results, failed_at_size

if __name__ == "__main__":
    # Test Gemma 2 26B
    tester = GemmaPerformanceTester("google/gemma-2-26b")
    results, failure_point = tester.run_full_test()
    
    # Print summary
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    for r in results:
        if r.get("status") == "success":
            print(f"Context: {r['context_size']:>6} | TPS: {r['tokens_per_second']:>6.1f} | "
                  f"Latency: {r['total_latency_ms']:>6}ms | Memory: {r['gpu_memory_peak_gb']:>5.1f}GB")
```

### 4. Running the Tests
```bash
# Activate environment
source .venv/bin/activate

# Run performance test
python test_performance.py

# Check logs
ls -lh logs/
tail -f logs/*.jsonl  # Watch results in real-time
```

---

## 📊 Results

### Gemma 2 26B Model

#### Performance by Context Size
| Context | TPS | Latency | Memory | Status |
|---------|-----|---------|--------|--------|
| 8K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| 16K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| 24K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| 32K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

**Point of Failure**: [TO FILL]

---

### Gemma 2 31B Model

#### Performance by Context Size
| Context | TPS | Latency | Memory | Status |
|---------|-----|---------|--------|--------|
| 8K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| 16K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| 24K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |
| 32K | [TO FILL] | [TO FILL] | [TO FILL] | [TO FILL] |

**Point of Failure**: [TO FILL]

---

### 26B vs 31B Comparison

**Speed Tradeoff**:
- 26B: Faster inference, lower latency
- 31B: Slower but better quality

**Memory Tradeoff**:
- 26B: ~[TO FILL]GB peak
- 31B: ~[TO FILL]GB peak

**Recommendation**: [TO FILL BASED ON USE CASE]

---

## 🔍 Key Findings

### Finding 1: [TO FILL]
- **What**: 
- **Why it matters**: 
- **Evidence**: 

### Finding 2: [TO FILL]
- **What**: 
- **Why it matters**: 
- **Evidence**: 

### Finding 3: [TO FILL]
- **What**: 
- **Why it matters**: 
- **Evidence**: 

---

## 🚀 Next Steps

### Immediate (Week 2-3)
- [ ] Multi-node clustering (4x DGX machines)
- [ ] Rerun performance tests in clustered mode
- [ ] Compare single-node vs distributed performance
- [ ] Test load balancing strategies

### Future (Production)
- [ ] API rate limiting & concurrency testing
- [ ] Multi-user load testing
- [ ] Cost-per-inference analysis
- [ ] Model quantization (int8/int4) for speed improvements

---

## 📚 References

- [vLLM Documentation](https://docs.vllm.ai/)
- [Gemma Model Card](https://huggingface.co/google/gemma-2-26b)
- [DGX A100 Specs](https://www.nvidia.com/content/dam/en-us/Solutions/data-center/a100/pdf/nvidia-a100-datasheet-nvidia.pdf)
- [Tailscale for Remote Access](https://tailscale.com/)

---

## 📞 Questions?

For technical details, see: `userstories.md`
For logs & raw data, see: `logs/` directory

**Last Updated**: [TO FILL]
