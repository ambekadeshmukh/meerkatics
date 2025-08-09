#!/usr/bin/env python3
# meerkatics/scripts/test_metrics_collection.py

import os
import sys
import time
import json
import uuid
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add SDK to path
SCRIPT_DIR = Path(__file__).parent
SDK_DIR = SCRIPT_DIR.parent / "sdk"
sys.path.append(str(SDK_DIR))

import meerkatics
from meerkatics.providers.openai import OpenAIMonitor
from meerkatics.metrics.token_counter import count_tokens

def generate_random_prompt():
    """Generate a random prompt to test with."""
    topics = [
        "artificial intelligence",
        "machine learning",
        "natural language processing",
        "computer vision",
        "distributed systems",
        "cloud computing",
        "quantum computing",
        "cybersecurity",
        "blockchain",
        "data science"
    ]
    
    actions = [
        "Explain",
        "Summarize",
        "Compare",
        "Contrast",
        "Define",
        "Describe",
        "Analyze",
        "Evaluate",
        "List benefits of",
        "Give examples of"
    ]
    
    qualifiers = [
        "in simple terms",
        "for beginners",
        "for experts",
        "in detail",
        "briefly",
        "with examples",
        "with use cases",
        "with pros and cons",
        "with historical context",
        "in the context of modern applications"
    ]
    
    topic = random.choice(topics)
    action = random.choice(actions)
    qualifier = random.choice(qualifiers)
    
    return f"{action} {topic} {qualifier}."

def test_metrics_collection(kafka_enabled=False):
    print("=== Testing Metrics Collection ===")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment variables.")
        api_key = "sk-dummy-key-for-testing"
        print(f"Using dummy API key for testing: {api_key}")
    
    # Initialize OpenAI monitor
    print("Initializing OpenAI monitor...")
    
    # Set up Kafka config if enabled
    kafka_config = None
    if kafka_enabled:
        kafka_config = {
            "bootstrap_servers": os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            "topic": "llm-monitoring"
        }
        print(f"Kafka integration enabled: {kafka_config}")
    
    # Create monitor
    monitor = OpenAIMonitor(
        api_key=api_key,
        model="gpt-3.5-turbo",
        application_name="meerkatics-metrics-test",
        environment="testing",
        log_requests=True,
        log_responses=True,
        kafka_config=kafka_config
    )
    
    # Mock OpenAI API call
    original_call = monitor.call
    
    def mock_call(prompt, client_function, **kwargs):
        """Mock the API call to avoid actual API usage."""
        # Simulate API latency
        latency = random.uniform(0.5, 2.0)
        time.sleep(latency)
        
        # Create mock response
        prompt_tokens = count_tokens(prompt, "gpt-3.5-turbo")
        completion = f"This is a mock response to: {prompt[:30]}..."
        completion_tokens = count_tokens(completion, "gpt-3.5-turbo")
        
        # Occasional errors for realism
        if random.random() < 0.05:  # 5% chance of error
            raise Exception("Mock API error: rate limit exceeded")
        
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": completion
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }
    
    # Replace the original call method with our mock
    monitor.call = mock_call
    
    # Generate and track test requests
    print("Generating test requests...")
    successful_requests = 0
    failed_requests = 0
    total_tokens = 0
    total_cost = 0
    latencies = []
    
    # Track requests over time
    start_time = time.time()
    num_requests = 20
    
    for i in range(1, num_requests + 1):
        try:
            prompt = generate_random_prompt()
            
            print(f"Request {i}/{num_requests}: {prompt}")
            
            request_start = time.time()
            response = monitor.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            request_time = time.time() - request_start
            
            print(f"Response: {response['choices'][0]['message']['content'][:50]}...")
            print(f"Tokens: {response['usage']['total_tokens']} | Latency: {request_time:.2f}s")
            
            successful_requests += 1
            total_tokens += response['usage']['total_tokens']
            latencies.append(request_time)
            
            # Calculate approximate cost (using OpenAI pricing for gpt-3.5-turbo)
            prompt_cost = response['usage']['prompt_tokens'] * 0.0015 / 1000
            completion_cost = response['usage']['completion_tokens'] * 0.002 / 1000
            request_cost = prompt_cost + completion_cost
            total_cost += request_cost
            
            # Add some variability to request timing
            time.sleep(random.uniform(0.2, 1.0))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            failed_requests += 1
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Success rate: {successful_requests / num_requests * 100:.1f}%")
    print(f"Total tokens: {total_tokens}")
    print(f"Average tokens per request: {total_tokens / successful_requests:.1f}")
    print(f"Total cost: ${total_cost:.6f}")
    print(f"Test duration: {total_duration:.2f} seconds")
    
    if latencies:
        print(f"Average latency: {sum(latencies) / len(latencies):.2f} seconds")
        print(f"Min latency: {min(latencies):.2f} seconds")
        print(f"Max latency: {max(latencies):.2f} seconds")
    
    print("\nMetrics have been collected and should be available in the monitoring system.")
    if kafka_enabled:
        print("Check Kafka topic 'llm-monitoring' for the metrics data.")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Test Meerkatics metrics collection")
    parser.add_argument("--kafka", action="store_true", help="Enable Kafka integration")
    
    args = parser.parse_args()
    
    print("=== Meerkatics Metrics Collection Test ===")
    print(f"Version: {meerkatics.__version__}")
    
    result = test_metrics_collection(kafka_enabled=args.kafka)
    
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())