#!/bin/bash
cd /Users/xxxyxxx/Desktop/job-agent/linkedin_pipeline

# Backup current file
cp analyzer_ai.py analyzer_ai.py.backup2

# Extract the core methods from old analyzer
echo 'Extracting description fetching from old analyzer...'

# Copy the old working analyzer and merge it
python3 << 'PYEND'
# Simple approach: manually construct the updated analyzer

header = '''"""AI-Powered Job Analyzer using Claude API
Provides intelligent job matching and cover letter generation"""

import json
import os
import re
from typing import Dict, Optional
from datetime import datetime
import time

# Selenium imports for job description fetching
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print('Warning: anthropic package not installed. Run: pip install anthropic')
'''

with open('analyzer_ai_with_selenium.py', 'w') as f:
    f.write(header)
    f.write('\n\nprint("Created header with imports")\n')

print('Step 1: Created header with all imports')
PYEND

echo 'Done'
