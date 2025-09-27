#!/usr/bin/env python3
from analyzer_ai import AIJobAnalyzer
import json

# Load jobs
with open('jobs_found.json', 'r') as f:
    jobs = json.load(f)

print(f'Loaded {len(jobs)} jobs')

# Test with first job
if jobs:
    job = jobs[0]
    print(f'\nTesting: {job.get("title", "Unknown")}')
    print(f'Company: {job.get("company", "Unknown")}')
    print(f'Current desc length: {len(job.get("description", ""))} chars')
    print(f'URL: {job.get("url", "None")}')
    
    # Try to initialize analyzer
    try:
        analyzer = AIJobAnalyzer()
        print('\nAnalyzer initialized successfully')
    except Exception as e:
        print(f'\nFailed to initialize: {e}')
