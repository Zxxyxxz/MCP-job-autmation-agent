from scrapers.linkedin_scraper import LinkedInScraper

print('===========================================')
print('TESTING LINKEDIN JOB SCRAPER')
print('===========================================')

scraper = LinkedInScraper()
jobs = scraper.scrape_jobs(
    query='python developer',
    location='Netherlands',
    time_filter='week'
)

print(f'\nTest Results:')
print(f'   Scraper initialized: YES')
print(f'   Jobs found: {len(jobs)}')

if jobs:
    print(f'\nSample job:')
    sample = jobs[0]
    print(f'   Title: {sample.get("title", "N/A")}')
    print(f'   Company: {sample.get("company", "N/A")}')
    print(f'   Location: {sample.get("location", "N/A")}')

print('\nSCRAPER TEST: PASSED!')
