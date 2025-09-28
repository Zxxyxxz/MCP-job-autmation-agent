# complete_job_scraper.py - FIXED version
import json
from datetime import datetime
from job_scraper import JobScraper
from indeed_selenium_scraper import scrape_indeed_with_selenium  # ADD THIS IMPORT!

class CompleteJobScraper:
    def scrape_all(self):
        """Scrape LinkedIn with BeautifulSoup, Indeed with Selenium"""
        all_jobs = []
        
        # LinkedIn - your existing method works
        scraper = JobScraper()
        linkedin_jobs = scraper.get_linkedin_public("software engineer", "Netherlands")
        all_jobs.extend(linkedin_jobs)
        
        # Indeed - use Selenium (now properly imported)
        indeed_jobs = scrape_indeed_with_selenium("software engineer", "Amsterdam")
        all_jobs.extend(indeed_jobs)
        
        # Save with timestamp
        filename = f"jobs_found.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(all_jobs)} total jobs to {filename}")
        print(f"  - LinkedIn: {len(linkedin_jobs)}")
        print(f"  - Indeed: {len(indeed_jobs)}")
        
        return all_jobs

# Run it
if __name__ == "__main__":
    scraper = CompleteJobScraper()
    all_jobs = scraper.scrape_all()