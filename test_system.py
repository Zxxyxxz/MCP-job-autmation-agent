#!/usr/bin/env python3
"""Complete system test"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("="*60)
print("SYSTEM COMPONENT TESTS")
print("="*60)

# Test 1: Database
print("\n1. Testing Database...")
try:
    from database.database import JobTracker
    tracker = JobTracker()
    print("   ✓ Database initialized")
    
    # Try to get job count
    jobs = tracker.get_all_jobs()
    print(f"   ✓ Database has {len(jobs) if jobs else 0} jobs")
except Exception as e:
    print(f"   ✗ Database error: {e}")

# Test 2: Check existing scraped data
print("\n2. Checking Scraped Data...")
import glob
json_files = sorted(glob.glob('data/linkedin_jobs*.json'))
if json_files:
    latest_file = json_files[-1]
    with open(latest_file, 'r') as f:
        jobs = json.load(f)
    print(f"   ✓ Found {len(jobs)} jobs in {Path(latest_file).name}")
    if jobs:
        sample_job = jobs[0]
        print(f"   Sample: {sample_job.get('title', 'N/A')} at {sample_job.get('company', 'N/A')}")
else:
    print("   ✗ No scraped data found")

# Test 3: Profile
print("\n3. Checking Profile...")
try:
    with open('config/yigit_profile.json', 'r') as f:
        profile = json.load(f)
    print(f"   ✓ Profile loaded: {profile.get('name', 'Unknown')}")
    print(f"   Skills: {', '.join(profile.get('skills', [])[:3])}...")
except Exception as e:
    print(f"   ✗ Profile error: {e}")

# Test 4: Claude API
print("\n4. Testing Claude API...")
try:
    from dotenv import load_dotenv
    import os
    
    load_dotenv('config/.env')
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key or 'YOUR-ACTUAL-KEY' in api_key:
        print("   ✗ Need real API key in config/.env")
    else:
        print("   ✓ API key configured")
        
        # Test actual Claude connection
        from analyzers.analyzer_ai import AIJobAnalyzer
        analyzer = AIJobAnalyzer()
        
        # Simple test
        test_desc = "Python developer with AI experience needed"
        print("   Testing Claude with sample job...")
        
        # This will actually call Claude API
        result = analyzer.analyze_job_fit({"description": test_desc, "title": "Test Job", "company": "Test Co"})
        if result:
            print("   ✓ Claude responded successfully!")
        else:
            print("   ✗ Claude returned empty response")
            
except ImportError as e:
    print(f"   ✗ Import error: {e}")
except Exception as e:
    print(f"   ✗ API error: {e}")

# Test 5: Pipeline
print("\n5. Testing Pipeline...")
try:
    from run_pipeline import main
    print("   ✓ Pipeline imports successfully")
except Exception as e:
    print(f"   ✗ Pipeline error: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
