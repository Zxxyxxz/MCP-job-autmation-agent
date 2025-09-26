"""
LinkedIn Job Scraper - Stable Version
Handles public LinkedIn job listings without authentication
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import logging

class LinkedInScraper:
    def __init__(self, config_path='../config/settings.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config['browser']['user_agent'],
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Setup logging
        logging.basicConfig(
            filename='../logs/scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def build_search_url(self, query, location, time_filter=None):
        """Build LinkedIn search URL with parameters"""
        base_url = 'https://www.linkedin.com/jobs/search/'
        
        # Time filters
        time_params = {
            '24h': 'r86400',
            'week': 'r604800',
            'month': 'r2592000'
        }
        
        params = {
            'keywords': query,
            'location': location,
            'trk': 'public_jobs_jobs-search-bar_search-submit',
            'position': 1,
            'pageNum': 0
        }
        
        # Add time filter if specified
        if time_filter and time_filter in time_params:
            params['f_TPR'] = time_params[time_filter]
        
        # Build URL
        url = base_url + '?'
        url += '&'.join([f"{k}={v}" for k, v in params.items()])
        
        # Add cache buster
        url += f"&refresh={random.randint(1000, 9999)}"
        
        return url
    
    def scrape_jobs(self, query=None, location=None, time_filter=None):
        """Main scraping function"""
        query = query or self.config['search_settings']['default_query']
        location = location or self.config['search_settings']['location']
        time_filter = time_filter or self.config['search_settings']['time_filter']
        
        url = self.build_search_url(query, location, time_filter)
        self.logger.info(f"Scraping: {url}")
        print(f"\n🔍 Searching LinkedIn: {query} in {location} (past {time_filter})")
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple selectors for job cards
            job_cards = soup.find_all('div', class_='base-card')
            if not job_cards:
                job_cards = soup.find_all('div', class_='job-search-card')
            if not job_cards:
                job_cards = soup.find_all('li', class_='result-card')
            
            print(f"✅ Found {len(job_cards)} job listings")
            
            jobs = []
            for card in job_cards[:self.config['search_settings']['max_jobs_per_search']]:
                job = self.extract_job_info(card)
                if job and job.get('url'):
                    jobs.append(job)
                    print(f"  ✓ {job['title'][:50]}... at {job['company']}")
            
            # Save results
            self.save_jobs(jobs)
            return jobs
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            print(f"❌ Error fetching jobs: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            print(f"❌ Unexpected error: {e}")
            return []
    
    def extract_job_info(self, card):
        """Extract job information from a card element"""
        try:
            job = {}
            
            # Title
            title_elem = card.find('h3', class_='base-search-card__title')
            if not title_elem:
                title_elem = card.find('h3', class_='job-search-card__title')
            job['title'] = title_elem.text.strip() if title_elem else 'Unknown Title'
            
            # Company
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            if not company_elem:
                company_elem = card.find('a', class_='hidden-nested-link')
            job['company'] = company_elem.text.strip() if company_elem else 'Unknown Company'
            
            # Location
            location_elem = card.find('span', class_='job-search-card__location')
            if not location_elem:
                location_elem = card.find('span', class_='job-result-card__location')
            job['location'] = location_elem.text.strip() if location_elem else 'Unknown Location'
            
            # URL
            link_elem = card.find('a', class_='base-card__full-link')
            if not link_elem:
                link_elem = card.find('a', href=True)
            
            if link_elem and link_elem.get('href'):
                job['url'] = link_elem['href']
                # Clean up URL
                if job['url'].startswith('/'):
                    job['url'] = 'https://www.linkedin.com' + job['url']
                # Remove tracking parameters
                if '?' in job['url']:
                    job['url'] = job['url'].split('?')[0]
            else:
                return None
            
            # Posted time
            time_elem = card.find('time')
            if time_elem:
                job['posted'] = time_elem.get('datetime', 'Unknown')
            else:
                time_elem = card.find('span', class_='job-search-card__listdate')
                job['posted'] = time_elem.text.strip() if time_elem else 'Unknown'
            
            # Job ID from URL
            import re
            job_id_match = re.search(r'/view/(\d+)', job.get('url', ''))
            job['job_id'] = job_id_match.group(1) if job_id_match else None
            
            job['scraped_at'] = datetime.now().isoformat()
            job['source'] = 'linkedin'
            
            return job
            
        except Exception as e:
            self.logger.warning(f"Failed to extract job info: {e}")
            return None
    
    def save_jobs(self, jobs):
        """Save jobs to JSON file"""
        if not jobs:
            return
        
        filename = f"../data/linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(jobs, f, indent=2)
        
        print(f"\n💾 Saved {len(jobs)} jobs to {filename}")
        self.logger.info(f"Saved {len(jobs)} jobs to {filename}")

if __name__ == '__main__':
    scraper = LinkedInScraper()
    jobs = scraper.scrape_jobs()
    print(f"\nTotal jobs scraped: {len(jobs)}")
