#!/usr/bin/env python3
"""Direct test of Claude API"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment
load_dotenv('config/.env')
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    print("No API key found!")
    exit()

print(f"API Key found: {api_key[:20]}...")

try:
    # Simple client initialization
    client = Anthropic(api_key=api_key)
    
    # Use CURRENT model
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Current Sonnet model
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'Hello, the API is working!' if you can read this."}
        ]
    )
    
    print(f"✅ Claude says: {response.content[0].text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
