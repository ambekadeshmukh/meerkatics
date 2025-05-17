#!/usr/bin/env python3
# sentinelops/scripts/test_providers.py

import os
import sys
import json
import time
import argparse
from pathlib import Path

# Add SDK to path
SCRIPT_DIR = Path(__file__).parent
SDK_DIR = SCRIPT_DIR.parent / "sdk"
sys.path.append(str(SDK_DIR))

import sentinelops
from sentinelops.providers.openai import OpenAIMonitor
from sentinelops.providers.anthropic import AnthropicMonitor
from sentinelops.providers.huggingface import HuggingFaceMonitor
from sentinelops.providers.bedrock import BedrockMonitor
from sentinelops.providers.cohere import CohereMonitor
from sentinelops.providers.vertex import VertexAIMonitor
from sentinelops.providers.replicate import ReplicateMonitor

def test_openai():
    print("\n=== Testing OpenAI Provider ===")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment variables. Skipping test.")
        return False
    
    try:
        print("Initializing OpenAI monitor...")
        monitor = OpenAIMonitor(
            api_key=api_key,
            model="gpt-3.5-turbo",
            application_name="sentinelops-test"
        )
        
        print("Testing chat completion...")
        response = monitor.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Summarize the importance of monitoring LLM applications in 2 sentences."}
            ]
        )
        
        print(f"Response: {response['choices'][0]['message']['content']}")
        print("✅ OpenAI test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ OpenAI test failed: {str(e)}")
        return False

def test_anthropic():
    print("\n=== Testing Anthropic Provider ===")
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not found in environment variables. Skipping test.")
        return False
    
    try:
        print("Initializing Anthropic monitor...")
        monitor = AnthropicMonitor(
            api_key=api_key,
            model="claude-2",
            application_name="sentinelops-test"
        )
        
        print("Testing completion...")
        response = monitor.completion(
            prompt="\n\nHuman: Summarize the importance of monitoring LLM applications in 2 sentences.\n\nAssistant:",
            max_tokens_to_sample=100
        )
        
        print(f"Response: {response['completion']}")
        print("✅ Anthropic test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Anthropic test failed: {str(e)}")
        return False

def test_huggingface():
    print("\n=== Testing HuggingFace Provider ===")
    
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        print("⚠️  HUGGINGFACE_API_KEY not found in environment variables. Skipping test.")
        return False
    
    try:
        print("Initializing HuggingFace monitor...")
        monitor = HuggingFaceMonitor(
            api_key=api_key,
            model="gpt2",
            application_name="sentinelops-test"
        )
        
        print("Testing text generation...")
        response = monitor.text_generation(
            prompt="Monitoring LLM applications is important because"
        )
        
        print(f"Response: {response[0]['generated_text']}")
        print("✅ HuggingFace test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ HuggingFace test failed: {str(e)}")
        return False

def test_bedrock():
    print("\n=== Testing AWS Bedrock Provider ===")
    
    # AWS credentials should be configured via ~/.aws/credentials or environment variables
    try:
        print("Initializing Bedrock monitor...")
        monitor = BedrockMonitor(
            model="anthropic.claude-v2",
            application_name="sentinelops-test"
        )
        
        print("Testing text generation...")
        response = monitor.completion(
            prompt="\n\nHuman: Summarize the importance of monitoring LLM applications in 2 sentences.\n\nAssistant:",
            max_tokens_to_sample=100
        )
        
        print(f"Response: {response['completion']}")
        print("✅ AWS Bedrock test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ AWS Bedrock test failed: {str(e)}")
        return False

def test_cohere():
    print("\n=== Testing Cohere Provider ===")
    
    api_key = os.environ.get("COHERE_API_KEY")
    if not api_key:
        print("⚠️  COHERE_API_KEY not found in environment variables. Skipping test.")
        return False
    
    try:
        print("Initializing Cohere monitor...")
        monitor = CohereMonitor(
            api_key=api_key,
            model="command",
            application_name="sentinelops-test"
        )
        
        print("Testing text generation...")
        response = monitor.generate(
            prompt="Summarize the importance of monitoring LLM applications in 2 sentences."
        )
        
        print(f"Response: {response.generations[0].text}")
        print("✅ Cohere test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Cohere test failed: {str(e)}")
        return False

def test_vertex():
    print("\n=== Testing Google Vertex AI Provider ===")
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("⚠️  GOOGLE_CLOUD_PROJECT not found in environment variables. Skipping test.")
        return False
    
    try:
        print("Initializing Vertex AI monitor...")
        monitor = VertexAIMonitor(
            model="gemini-pro",
            application_name="sentinelops-test",
            project_id=project_id
        )
        
        print("Testing text generation...")
        response = monitor.text_generation(
            prompt="Summarize the importance of monitoring LLM applications in 2 sentences."
        )
        
        print(f"Response: {response['text']}")
        print("✅ Google Vertex AI test completed successfully!")
        return True
    except Exception as e:
       print(f"❌ Google Vertex AI test failed: {str(e)}")
       return False

def test_replicate():
   print("\n=== Testing Replicate Provider ===")
   
   api_token = os.environ.get("REPLICATE_API_TOKEN")
   if not api_token:
       print("⚠️  REPLICATE_API_TOKEN not found in environment variables. Skipping test.")
       return False
   
   try:
       print("Initializing Replicate monitor...")
       monitor = ReplicateMonitor(
           api_token=api_token,
           model="meta/llama-2-70b-chat",
           application_name="sentinelops-test"
       )
       
       print("Testing run...")
       response = monitor.run(
           prompt="Summarize the importance of monitoring LLM applications in 2 sentences.",
           input_params={
               "temperature": 0.7,
               "max_new_tokens": 100
           }
       )
       
       print(f"Response: {''.join(response)}")
       print("✅ Replicate test completed successfully!")
       return True
   except Exception as e:
       print(f"❌ Replicate test failed: {str(e)}")
       return False

def test_batching():
   print("\n=== Testing Batching Functionality ===")
   
   api_key = os.environ.get("OPENAI_API_KEY")
   if not api_key:
       print("⚠️  OPENAI_API_KEY not found in environment variables. Skipping test.")
       return False
   
   try:
       print("Initializing OpenAI monitor with batching...")
       monitor = OpenAIMonitor(
           api_key=api_key,
           model="gpt-3.5-turbo",
           application_name="sentinelops-test",
           enable_batching=True,
           batch_size=3,
           flush_interval=2.0
       )
       
       print("Testing multiple requests with batching...")
       prompts = [
           "What is monitoring?",
           "Why is observability important?",
           "How do LLMs work?",
           "What is the difference between metrics and logs?",
           "What is distributed tracing?"
       ]
       
       for i, prompt in enumerate(prompts, 1):
           print(f"Request {i}/{len(prompts)}: {prompt}")
           response = monitor.chat_completion(
               messages=[
                   {"role": "user", "content": prompt}
               ]
           )
           print(f"Response {i}: {response['choices'][0]['message']['content'][:50]}...")
           
           # Small delay to see batching in action
           if i < len(prompts):
               print(f"Waiting for more requests to batch...")
               time.sleep(0.5)
       
       # Final flush to ensure all data is sent
       print("Flushing remaining batch data...")
       monitor.batch_processor.flush()
       
       print("✅ Batching test completed successfully!")
       return True
   except Exception as e:
       print(f"❌ Batching test failed: {str(e)}")
       return False

def test_caching():
   print("\n=== Testing Caching Functionality ===")
   
   api_key = os.environ.get("OPENAI_API_KEY")
   if not api_key:
       print("⚠️  OPENAI_API_KEY not found in environment variables. Skipping test.")
       return False
   
   try:
       print("Initializing OpenAI monitor with caching...")
       monitor = OpenAIMonitor(
           api_key=api_key,
           model="gpt-3.5-turbo",
           application_name="sentinelops-test",
           enable_caching=True,
           cache_ttl=60,  # 1 minute
           cache_max_size=100
       )
       
       test_prompt = "Explain caching in one sentence."
       messages = [
           {"role": "user", "content": test_prompt}
       ]
       
       print("First request (should be a cache miss)...")
       start_time = time.time()
       response1 = monitor.chat_completion(messages=messages)
       time1 = time.time() - start_time
       print(f"Response: {response1['choices'][0]['message']['content']}")
       print(f"Request time: {time1:.3f} seconds")
       
       print("\nSecond request with same prompt (should be a cache hit)...")
       start_time = time.time()
       response2 = monitor.chat_completion(messages=messages)
       time2 = time.time() - start_time
       print(f"Response: {response2['choices'][0]['message']['content']}")
       print(f"Request time: {time2:.3f} seconds")
       
       if time2 < time1:
           print(f"✅ Caching is working! (First request: {time1:.3f}s, Second request: {time2:.3f}s)")
       else:
           print(f"⚠️  Caching may not be working as expected. Time comparison: First: {time1:.3f}s, Second: {time2:.3f}s")
       
       # Test cache invalidation with different parameters
       print("\nThird request with different parameters (should be a cache miss)...")
       start_time = time.time()
       response3 = monitor.chat_completion(
           messages=messages,
           temperature=0.9  # Different parameter
       )
       time3 = time.time() - start_time
       print(f"Response: {response3['choices'][0]['message']['content']}")
       print(f"Request time: {time3:.3f} seconds")
       
       if time3 > time2:
           print(f"✅ Cache invalidation is working! (Cache hit: {time2:.3f}s, Different params: {time3:.3f}s)")
       else:
           print(f"⚠️  Cache invalidation may not be working as expected. Times: Cache hit: {time2:.3f}s, Different params: {time3:.3f}s")
       
       print("✅ Caching test completed!")
       return True
   except Exception as e:
       print(f"❌ Caching test failed: {str(e)}")
       return False

def main():
   parser = argparse.ArgumentParser(description="Test SentinelOps provider integrations")
   parser.add_argument("--provider", choices=["all", "openai", "anthropic", "huggingface", "bedrock", "cohere", "vertex", "replicate", "batching", "caching"], default="all", help="Provider to test")
   
   args = parser.parse_args()
   
   print("=== SentinelOps Provider Integration Test ===")
   print(f"Version: {sentinelops.__version__}")
   print(f"Testing provider: {args.provider}")
   
   results = {}
   
   if args.provider in ["all", "openai"]:
       results["OpenAI"] = test_openai()
   
   if args.provider in ["all", "anthropic"]:
       results["Anthropic"] = test_anthropic()
   
   if args.provider in ["all", "huggingface"]:
       results["HuggingFace"] = test_huggingface()
   
   if args.provider in ["all", "bedrock"]:
       results["AWS Bedrock"] = test_bedrock()
   
   if args.provider in ["all", "cohere"]:
       results["Cohere"] = test_cohere()
   
   if args.provider in ["all", "vertex"]:
       results["Google Vertex AI"] = test_vertex()
   
   if args.provider in ["all", "replicate"]:
       results["Replicate"] = test_replicate()
   
   if args.provider in ["all", "batching"]:
       results["Batching"] = test_batching()
   
   if args.provider in ["all", "caching"]:
       results["Caching"] = test_caching()
   
   print("\n=== Test Results ===")
   all_passed = True
   for provider, result in results.items():
       status = "✅ PASSED" if result else "❌ FAILED"
       print(f"{provider}: {status}")
       if not result:
           all_passed = False
   
   return 0 if all_passed else 1

if __name__ == "__main__":
   sys.exit(main())