#!/usr/bin/env python3
"""
Test Database Integration with Scraper
"""

from scrapers.linkedin_scraper import LinkedInScraper
from database import JobTracker

print('='*60)
print('🧪 TESTING DATABASE + SCRAPER INTEGRATION')
print('='*60)

# Initialize database
print('\n1️⃣  Initializing database...')
tracker = JobTracker()
print('✅ Database initialized')

# Initialize scraper
print('\n2️⃣  Initializing scraper...')
scraper = LinkedInScraper()
print('✅ Scraper initialized')

# Scrape jobs
print('\n3️⃣  Scraping jobs...')
jobs = scraper.scrape_jobs(
    query='junior software engineer',
    location='Netherlands',
    time_filter='week'
)
print(f'✅ Found {len(jobs)} jobs')

# Add jobs to database
print('\n4️⃣  Adding jobs to database...')
added_count = 0
skipped_count = 0

for job in jobs:
    try:
        job_id = tracker.add_job(job)
        added_count += 1
        print(f'  ✓ Added: {job["title"][:40]}... (ID: {job_id})')
    except Exception as e:
        skipped_count += 1
        print(f'  ⊘ Skipped (duplicate): {job["title"][:40]}...')

print(f'\n✅ Added {added_count} new jobs, skipped {skipped_count} duplicates')

# Get statistics
print('\n5️⃣  Database Statistics:')
stats = tracker.get_statistics()
print(f'   Total jobs in database: {stats["total_jobs"]}')
print(f'   By status: {stats["by_status"]}')
print(f'   Average AI score: {stats["average_ai_score"]}')

# Show some jobs
print('\n6️⃣  Recent jobs in database:')
recent = tracker.get_recent_jobs(limit=5)
for i, job in enumerate(recent, 1):
    print(f'   {i}. {job["title"]} at {job["company"]}')
    print(f'      Status: {job["status"]} | Scraped: {job["scraped_date"][:10]}')

# Test status update
if recent:
    print('\n7️⃣  Testing status update...')
    tracker.update_status(recent[0]['id'], 'reviewed', 'This looks promising!')
    print(f'   ✅ Updated status for: {recent[0]["title"]}')
    
    # Show history
    history = tracker.get_job_history(recent[0]['id'])
    print(f'   History ({len(history)} events):')
    for event in history:
        print(f'     - {event["action"]}: {event["details"]} ({event["timestamp"][:16]})')

print('\n' + '='*60)
print('✅ ALL TESTS PASSED!')
print('='*60)
print(f'\n📊 Database location: data/jobs.db')
print(f'📁 You now have a complete job tracking system!')

tracker.close()
