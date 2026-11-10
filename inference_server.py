#!/usr/bin/env python3
"""
On-Demand Gemma Inference Server
- FastAPI-based REST API
- vLLM for efficient inference
- Request-based (no idle waste)
- Configurable for any HuggingFace model
- Logging & metrics
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer


# ============================================================================
# Configuration
# ============================================================================

MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-2-26b")
GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.9"))
MAX_MODEL_LEN = int(os.getenv("MAX_MODEL_LEN", "32768"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
LOG_DIR = Path(os.getenv("LOG_DIR", "./logs"))

LOG_DIR.mkdir(exist_ok=True)

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "inference_server.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ============================================================================
# Request/Response Models
# ============================================================================

class GenerationRequest(BaseModel):
    """Request body for text generation"""
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50


class GenerationResponse(BaseModel):
    """Response body for text generation"""
    prompt: str
    generated_text: str
    prompt_tokens: int
    generated_tokens: int
    latency_ms: float
    tokens_per_second: float
    model: str
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model: str
    gpu_available: bool
    timestamp: str


# ============================================================================
# Global State
# ============================================================================

app = FastAPI(
    title="Gemma Inference Server",
    description="On-demand inference API for Gemma models",
    version="1.0.0",
)

# Lazy loading - model loads on first request
llm_instance = None
tokenizer_instance = None
request_count = 0


# ============================================================================
# Initialization
# ============================================================================

def load_model():
    """Load model on first request (lazy loading)"""
    global llm_instance, tokenizer_instance
    
    if llm_instance is not None:
        return  # Already loaded
    
    logger.info(f"Loading model: {MODEL_NAME}")
    
    try:
        llm_instance = LLM(
            model=MODEL_NAME,
            gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
            max_model_len=MAX_MODEL_LEN,
            tensor_parallel_size=1,
        )
        
        tokenizer_instance = AutoTokenizer.from_pretrained(MODEL_NAME)
        
        logger.info(f"✅ Model loaded successfully: {MODEL_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        raise


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint (doesn't load model)"""
    return HealthResponse(
        status="ok",
        model=MODEL_NAME,
        gpu_available=True,
        timestamp=datetime.now().isoformat(),
    )


@app.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check (loads model if needed)"""
    try:
        load_model()
        return HealthResponse(
            status="ready",
            model=MODEL_NAME,
            gpu_available=True,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Model not ready: {str(e)}")


@app.post("/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate text completion for given prompt
    
    Model is loaded on first request, then kept in memory for subsequent requests.
    """
    global request_count
    request_count += 1
    
    try:
        # Load model on first request
        load_model()
        
        logger.info(f"[Request #{request_count}] Generating for prompt: {request.prompt[:100]}...")
        
        # Tokenize prompt to count tokens
        prompt_tokens = len(tokenizer_instance.encode(request.prompt))
        
        if prompt_tokens > MAX_MODEL_LEN:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt too long: {prompt_tokens} tokens (max: {MAX_MODEL_LEN})",
            )
        
        # Setup sampling parameters
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            max_tokens=request.max_tokens,
        )
        
        # Generate
        start_time = time.time()
        outputs = llm_instance.generate(
            request.prompt,
            sampling_params,
        )
        latency = time.time() - start_time
        
        # Extract output
        output_text = outputs[0].outputs[0].text
        output_tokens = len(tokenizer_instance.encode(output_text))
        
        # Calculate metrics
        tps = output_tokens / latency if latency > 0 else 0
        latency_ms = int(latency * 1000)
        
        response = GenerationResponse(
            prompt=request.prompt,
            generated_text=output_text,
            prompt_tokens=prompt_tokens,
            generated_tokens=output_tokens,
            latency_ms=latency_ms,
            tokens_per_second=round(tps, 2),
            model=MODEL_NAME,
            timestamp=datetime.now().isoformat(),
        )
        
        # Log result to JSON file
        log_entry = response.dict()
        log_file = LOG_DIR / f"requests_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        async def log_request():
            """Background task to log request"""
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        
        background_tasks.add_task(log_request)
        
        logger.info(
            f"[Request #{request_count}] ✅ Generated {output_tokens} tokens "
            f"in {latency_ms}ms ({tps:.1f} TPS)"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Request #{request_count}] ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get server statistics"""
    return {
        "total_requests": request_count,
        "model": MODEL_NAME,
        "gpu_memory_utilization_target": GPU_MEMORY_UTILIZATION,
        "max_model_length": MAX_MODEL_LEN,
        "model_loaded": llm_instance is not None,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/unload")
async def unload_model():
    """Manually unload model to free GPU memory"""
    global llm_instance, tokenizer_instance
    
    try:
        if llm_instance is not None:
            del llm_instance
            del tokenizer_instance
            llm_instance = None
            tokenizer_instance = None
            logger.info("✅ Model unloaded from GPU")
            return {"status": "unloaded", "model": MODEL_NAME}
        else:
            return {"status": "not_loaded", "model": MODEL_NAME}
    except Exception as e:
        logger.error(f"Error unloading model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to unload: {str(e)}")


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Log server startup"""
    logger.info("=" * 80)
    logger.info(f"Inference Server Starting")
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"GPU Memory Utilization: {GPU_MEMORY_UTILIZATION}")
    logger.info(f"Max Model Length: {MAX_MODEL_LEN}")
    logger.info(f"Server: {HOST}:{PORT}")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown():
    """Log server shutdown and cleanup"""
    global llm_instance, tokenizer_instance
    
    logger.info("=" * 80)
    logger.info(f"Inference Server Shutting Down")
    logger.info(f"Total Requests Processed: {request_count}")
    logger.info("=" * 80)
    
    if llm_instance is not None:
        del llm_instance
        del tokenizer_instance


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Uvicorn server...")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )
