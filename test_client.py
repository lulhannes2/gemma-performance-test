#!/usr/bin/env python3
"""
Test client for Gemma Inference Server
- Send requests to running server
- Measure performance
- Log results
"""

import requests
import json
import time
import argparse
from datetime import datetime
from pathlib import Path


def test_inference(base_url: str, prompt: str, model_version: str = "26b"):
    """Send request to inference server"""
    
    url = f"{base_url}/generate"
    
    payload = {
        "prompt": prompt,
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
    }
    
    print(f"\n{'='*80}")
    print(f"Testing Gemma {model_version} - {datetime.now().isoformat()}")
    print(f"{'='*80}")
    print(f"Prompt: {prompt[:100]}...")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        elapsed = time.time() - start
        
        print(f"\n✅ Response Received ({elapsed:.1f}s total)")
        print(f"\nGenerated Text:\n{'-'*80}")
        print(result['generated_text'])
        print(f"{'-'*80}")
        
        print(f"\nMetrics:")
        print(f"  Prompt Tokens:        {result['prompt_tokens']}")
        print(f"  Generated Tokens:     {result['generated_tokens']}")
        print(f"  Latency:              {result['latency_ms']}ms")
        print(f"  Tokens/Second:        {result['tokens_per_second']}")
        print(f"  Model:                {result['model']}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Server not running at {base_url}")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Request took too long")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None


def test_health(base_url: str):
    """Check server health"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Server Health: {data['status']}")
            print(f"   Model: {data['model']}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test Gemma Inference Server")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of inference server"
    )
    parser.add_argument(
        "--model",
        default="26b",
        choices=["26b", "31b"],
        help="Which model to test"
    )
    parser.add_argument(
        "--prompt",
        default="Explain the benefits of large language models in production environments.",
        help="Prompt to send"
    )
    parser.add_argument(
        "--health-only",
        action="store_true",
        help="Only run health check"
    )
    
    args = parser.parse_args()
    
    # Adjust URL for model
    url = args.url.replace(":8000", "")
    if args.model == "31b":
        url = url + ":8001"
    else:
        url = url + ":8000"
    
    print(f"\nGemma Inference Server - Test Client")
    print(f"{'='*80}")
    print(f"Connecting to: {url}")
    
    # Health check
    if not test_health(url):
        print("\nServer is not responding. Make sure it's running:")
        print(f"  docker-compose up gemma-26b")
        return
    
    if args.health_only:
        print("\n✅ Server is healthy!")
        return
    
    # Run test
    result = test_inference(url, args.prompt, args.model)
    
    if result:
        print(f"\n✅ Test Complete!")


if __name__ == "__main__":
    main()
