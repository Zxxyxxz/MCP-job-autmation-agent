#!/usr/bin/env python3
"""Pre-Test System Check"""

import os
import sys

print('\n' + '='*60)
print('🔍 PRE-TEST SYSTEM CHECK')
print('='*60 + '\n')

# Check 1: Python packages
print('1️⃣  Checking Python packages...')
packages = ['requests', 'beautifulsoup4', 'anthropic']
all_installed = True
for pkg in packages:
    try:
        if pkg == 'beautifulsoup4':
            __import__('bs4')
            print(f'   ✅ {pkg} installed')
        else:
            __import__(pkg)
            print(f'   ✅ {pkg} installed')
    except ImportError:
        print(f'   ❌ {pkg} NOT installed')
        all_installed = False

if not all_installed:
    print('\n   ⚠️  Install missing packages: pip3 install requests beautifulsoup4 anthropic')
    sys.exit(1)

# Check 2: API Key
print('\n2️⃣  Checking API key...')
api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    if api_key.startswith('sk-ant-'):
        print(f'   ✅ API key is set ({len(api_key)} characters)')
        print(f'   ✅ Key format looks correct (starts with sk-ant-)')
    else:
        print(f'   ⚠️  API key is set but format looks wrong')
        print(f'   Expected to start with: sk-ant-')
        print(f'   Your key starts with: {api_key[:10]}...')
else:
    print('   ❌ API key NOT set')
    print('   ⚠️  Set it with: export ANTHROPIC_API_KEY="your-key-here"')
    sys.exit(1)

# Check 3: Project files
print('\n3️⃣  Checking project files...')
required_files = [
    'database.py',
    'analyzer_ai.py',
    'scrapers/linkedin_scraper.py',
    'test_full_pipeline.py',
    'yigit_profile.json',
    'config/settings.json'
]
all_exist = True
for file in required_files:
    if os.path.exists(file):
        print(f'   ✅ {file}')
    else:
        print(f'   ❌ {file} MISSING')
        all_exist = False

if not all_exist:
    print('\n   ⚠️  Some files are missing!')
    sys.exit(1)

# Check 4: Database
print('\n4️⃣  Checking database...')
if os.path.exists('data/jobs.db'):
    import sqlite3
    conn = sqlite3.connect('data/jobs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM jobs')
    count = cursor.fetchone()[0]
    conn.close()
    print(f'   ✅ Database exists with {count} jobs')
else:
    print('   ⚠️  Database not found (will be created on first run)')

# Check 5: Internet connection
print('\n5️⃣  Checking internet connection...')
try:
    import requests
    response = requests.get('https://www.linkedin.com', timeout=5)
    if response.status_code == 200:
        print('   ✅ Internet connection working')
    else:
        print(f'   ⚠️  LinkedIn returned status {response.status_code}')
except Exception as e:
    print(f'   ❌ Internet connection failed: {e}')
    sys.exit(1)

print('\n' + '='*60)
print('✅ ALL CHECKS PASSED - READY TO TEST!')
print('='*60)
print('\nNext step: python3 test_full_pipeline.py\n')
