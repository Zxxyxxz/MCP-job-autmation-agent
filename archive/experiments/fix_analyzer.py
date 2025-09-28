# This script recreates analyzer_ai.py with correct escaping

content = '''"""AI-Powered Job Analyzer using Claude API
Provides intelligent job matching and cover letter generation"""

import json
import os
import re
from typing import Dict, Optional
from datetime import datetime

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print('Warning: anthropic package not installed. Run: pip install anthropic')


class AIJobAnalyzer:
    """Use Claude to analyze job fit and generate application materials"""
    
    def __init__(self, api_key: Optional[str] = None, profile_path: str = 'yigit_profile.json'):
        """Initialize analyzer with Claude API"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError('anthropic package not installed. Install with: pip install anthropic')
        
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                'Anthropic API key required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.\n'
                'Get your key at: https://console.anthropic.com/'
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Load candidate profile
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        
        print('AI Analyzer initialized with Claude API')
'''

# Write to file
with open('analyzer_ai.py', 'w') as f:
    f.write(content)

print('Created first part of analyzer_ai.py')
