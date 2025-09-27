#!/usr/bin/env python3
"""
Comprehensive test suite for job-agent project
Tests all core components before reorganization
"""

import sys
import json
from datetime import datetime

print('=' * 70)
print('JOB AGENT - COMPONENT TESTING')
print('=' * 70)
print()

# Test results tracking
results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test_result(name, passed, message=''):
    if passed:
        results['passed'].append(name)
        print(f'✓ {name}')
        if message:
            print(f'  {message}')
    else:
        results['failed'].append(name)
        print(f'✗ {name}')
        if message:
            print(f'  ERROR: {message}')
    print()

# TEST 1: Import all core modules
print('TEST 1: Module Imports')
print('-' * 70)

try:
    from scrapers.linkedin_scraper import LinkedInScraper
    test_result('Import LinkedInScraper', True)
except Exception as e:
    test_result('Import LinkedInScraper', False, str(e))

try:
    from database import JobTracker
    test_result('Import JobTracker', True)
except Exception as e:
    test_result('Import JobTracker', False, str(e))

try:
    from analyzer_ai import AIJobAnalyzer
    test_result('Import AIJobAnalyzer', True)
except Exception as e:
    test_result('Import AIJobAnalyzer', False, str(e))

# TEST 2: LinkedIn Scraper
print('TEST 2: LinkedIn Scraper')
print('-' * 70)

try:
    scraper = LinkedInScraper()
    test_result('Initialize LinkedInScraper', True)
    
    # Test scraping (small batch)
    jobs = scraper.scrape_jobs('python', 'Netherlands', 'week')
    if len(jobs) > 0:
        test_result('Scrape jobs', True, f'Found {len(jobs)} jobs')
        
        # Verify job structure
        first_job = jobs[0]
        required_fields = ['title', 'company', 'url']
        missing = [f for f in required_fields if f not in first_job]
        
        if not missing:
            test_result('Job structure validation', True, 
                       f'Job has all required fields: {list(first_job.keys())}')
        else:
            test_result('Job structure validation', False,
                       f'Missing fields: {missing}')
    else:
        test_result('Scrape jobs', False, 'No jobs returned')
        
except Exception as e:
    test_result('LinkedIn Scraper test', False, str(e))

# TEST 3: Database Operations
print('TEST 3: Database Operations')
print('-' * 70)

try:
    tracker = JobTracker()
    test_result('Initialize JobTracker', True)
    
    # Test adding a job
    test_job = {
        'title': 'Test Job',
        'company': 'Test Company',
        'url': 'https://test.com/job/12345',
        'location': 'Test Location',
        'description': 'Test description',
        'job_id': 'test_12345'
    }
    
    try:
        job_id = tracker.add_job(test_job)
        test_result('Add job to database', True, f'Job ID: {job_id}')
    except Exception as e:
        # May fail if duplicate - that's OK
        if 'UNIQUE constraint' in str(e):
            test_result('Add job to database', True, 'Duplicate handling works')
        else:
            test_result('Add job to database', False, str(e))
    
    # Test retrieving jobs
    recent = tracker.get_recent_jobs(limit=5)
    test_result('Retrieve recent jobs', len(recent) > 0, 
               f'Found {len(recent)} jobs in database')
    
    # Test statistics
    stats = tracker.get_statistics()
    test_result('Get statistics', True,
               f'Total jobs: {stats.get("total_jobs", 0)}, '
               f'Avg score: {stats.get("average_ai_score", 0)}')
    
except Exception as e:
    test_result('Database operations', False, str(e))

# TEST 4: Analyzer (with API key check)
print('TEST 4: AI Analyzer')
print('-' * 70)

import os
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    test_result('API key check', False, 'ANTHROPIC_API_KEY not set')
else:
    test_result('API key check', True, 'API key found in environment')
    
    try:
        # Try to initialize analyzer
        analyzer = AIJobAnalyzer()
        test_result('Initialize AIJobAnalyzer', True)
        
        # Check if driver initialized
        if hasattr(analyzer, 'driver') and analyzer.driver:
            test_result('Selenium driver setup', True)
        else:
            test_result('Selenium driver setup', False, 'Driver not initialized')
        
        # Check cookie status
        if hasattr(analyzer, 'linkedin_authenticated'):
            if analyzer.linkedin_authenticated:
                test_result('LinkedIn authentication', True, 
                           'Cookies loaded and validated')
            else:
                results['warnings'].append('LinkedIn cookies not authenticated')
                test_result('LinkedIn authentication', False,
                           'Cookies present but authentication unclear')
        
    except Exception as e:
        test_result('AI Analyzer initialization', False, str(e))

# TEST 5: File Structure Check
print('TEST 5: File Structure')
print('-' * 70)

import os
critical_files = [
    'analyzer_ai.py',
    'database.py',
    'scrapers/linkedin_scraper.py',
    'config/settings.json',
    'yigit_profile.json'
]

for file in critical_files:
    exists = os.path.exists(file)
    test_result(f'File exists: {file}', exists)

# TEST 6: Configuration
print('TEST 6: Configuration Files')
print('-' * 70)

try:
    with open('config/settings.json', 'r') as f:
        config = json.load(f)
    test_result('Load settings.json', True,
               f'Config keys: {list(config.keys())}')
except Exception as e:
    test_result('Load settings.json', False, str(e))

try:
    with open('yigit_profile.json', 'r') as f:
        profile = json.load(f)
    test_result('Load yigit_profile.json', True,
               f'Profile has {len(profile.get("skills", {}).get("languages", []))} languages')
except Exception as e:
    test_result('Load yigit_profile.json', False, str(e))

# SUMMARY
print('=' * 70)
print('TEST SUMMARY')
print('=' * 70)
print()
print(f'✓ Passed: {len(results["passed"])}')
print(f'✗ Failed: {len(results["failed"])}')
print(f'⚠ Warnings: {len(results["warnings"])}')
print()

if results['failed']:
    print('Failed tests:')
    for test in results['failed']:
        print(f'  - {test}')
    print()

if results['warnings']:
    print('Warnings:')
    for warning in results['warnings']:
        print(f'  - {warning}')
    print()

# Overall status
if not results['failed']:
    print('STATUS: ALL TESTS PASSED ✓')
    print('Project is ready for reorganization.')
    sys.exit(0)
else:
    print('STATUS: SOME TESTS FAILED ✗')
    print('Fix issues before reorganizing.')
    sys.exit(1)
