#!/usr/bin/env python3
"""
AI-Powered Job Search Agent
Main entry point for the application
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from run_pipeline import main

if __name__ == '__main__':
    main()
