#!/usr/bin/env python
# Example of using Meerkatics SDK with OpenAI

import os
import time
from meerkatics.sdk import OpenAIMonitor

# Initialize the OpenAI monitor
monitor = OpenAIMonitor(
    api_key=os.environ.get("OPENAI_API_KEY"),
    application_name="demo-app",
    environment="development",
    log_requests=True,
    log_responses=True
)

def run_example():
    """Run a simple example using the Meerkatics SDK with OpenAI."""
    print("Running Meerkatics SDK example with OpenAI...")
    
    # Example messages for chat completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about LLM monitoring and observability."}
    ]
    
    # Start time for manual timing
    start_time = time.time()
    
    try:
        # Make API call through the monitor
        response = monitor.chat_completion(messages=messages, model="gpt-3.5-turbo")
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Print response
        print(f"\nResponse received in {elapsed_time:.2f} seconds:")
        print(f"Model: {response.model}")
        print(f"Response: {response.choices[0].message.content}")
        
        # Print metrics collected by Meerkatics
        print("\nMetrics collected by Meerkatics:")
        print(f"Request ID: {monitor.last_request_id}")
        print(f"Tokens Used: {monitor.last_token_count}")
        print(f"Estimated Cost: ${monitor.last_cost:.6f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_example()
