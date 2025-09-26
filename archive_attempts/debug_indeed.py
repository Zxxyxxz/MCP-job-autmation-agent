# debug_indeed.py - See what URLs we're getting
from job_scraper import JobScraper

scraper = JobScraper()
indeed_jobs = scraper.get_indeed_nl("software engineer", "Amsterdam")

print(f"\n🔍 Checking URL status for {len(indeed_jobs)} jobs:\n")
for i, job in enumerate(indeed_jobs[:5], 1):
    print(f"{i}. {job['title']}")
    print(f"   Company: {job['company']}")
    print(f"   URL: '{job.get('url', 'NO URL KEY')}'")
    print(f"   URL empty? {job.get('url', '') == ''}")
    print()