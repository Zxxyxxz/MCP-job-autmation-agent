#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, 'src')

# Check if analyzer has description fetching
from analyzers.analyzer_ai import AIJobAnalyzer

# List all methods
analyzer = AIJobAnalyzer()
methods = [m for m in dir(analyzer) if not m.startswith('_')]
print("Analyzer methods:", methods)

# Check for Selenium
import importlib.util
if importlib.util.find_spec("selenium"):
    print("\n✓ Selenium is installed")
    
# Look for fetch methods
fetch_methods = [m for m in methods if 'fetch' in m.lower() or 'get' in m.lower() or 'scrap' in m.lower()]
if fetch_methods:
    print(f"\nFound fetching methods: {fetch_methods}")
