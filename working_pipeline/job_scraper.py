# job_scraper.py
import requests
from bs4 import BeautifulSoup
import feedparser
import json
from datetime import datetime

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def get_linkedin_public(self, query="software engineer", location="Netherlands", time_filter="24h"):
        """Get LinkedIn jobs with time filtering"""
        print(f"🔍 Searching LinkedIn for: {query} in {location} (past {time_filter})")
        
        # Add time filter to URL
        time_param = {
            "24h": "&f_TPR=r86400",      # Past 24 hours
            "week": "&f_TPR=r604800",     # Past week  
            "month": "&f_TPR=r2592000"    # Past month
        }
        
        base_url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}"
        url = base_url + time_param.get(time_filter, "")
        
        # Add timestamp to avoid caching
        import random
        url += f"&refresh={random.randint(1000,9999)}"
        
        try:
            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            jobs = []
            
            # LinkedIn's actual class names (they change these!)
            job_cards = soup.find_all('div', class_='base-card')
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('li', attrs={'data-result-card-type': 'job'})
            
            print(f"Found {len(job_cards)} job cards")
            
            for card in job_cards[:25]:  # Limit to 25
                try:
                    # Extract what we can find
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if title_elem and company_elem:
                        job = {
                            'title': title_elem.text.strip() if title_elem else 'N/A',
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'location': location_elem.text.strip() if location_elem else location,
                            'url': link_elem.get('href', '') if link_elem else '',
                            'source': 'LinkedIn',
                            'date_scraped': datetime.now().isoformat()
                        }
                        jobs.append(job)
                        print(f"  ✓ {job['title']} at {job['company']}")
                except Exception as e:
                    continue
            
            return jobs
            
        except Exception as e:
            print(f"❌ LinkedIn scraping failed: {e}")
            return []
    
   # In job_scraper.py, replace the get_indeed_nl function:
    # In job_scraper.py - REPLACE get_indeed_nl with this WORKING version:

    def get_indeed_nl(self, query="software engineer", location="Netherlands"):
        """Working Indeed NL scraper with correct selectors"""
        print(f"\n🔍 Searching Indeed NL for: {query} in {location}")
        
        import urllib.parse
        import requests
        from bs4 import BeautifulSoup
        
        # Build Indeed NL URL (Dutch site)
        query_encoded = urllib.parse.quote(query)
        location_encoded = urllib.parse.quote(location)
        
        url = f"https://nl.indeed.com/jobs?q={query_encoded}&l={location_encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8'  # Dutch language
        }
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            jobs = []
            
            # Indeed NL uses these selectors - check for multiple possibilities
            job_cards = soup.find_all('div', class_='resultContent') or \
                    soup.find_all('div', class_='jobsearch-ResultsList') or \
                    soup.find_all('div', {'class': lambda x: x and 'result' in x.lower()})
            
            # If still no cards, try looking for links with job titles
            if not job_cards:
                # Alternative: find all job title links
                job_links = soup.find_all('a', {'data-testid': 'job-title'}) or \
                        soup.find_all('h2', class_='jobTitle')
                
                print(f"  Found {len(job_links)} job links")
                
                for link in job_links[:25]:
                    try:
                        # Get parent container
                        card = link.find_parent('div', class_=lambda x: x and 'job' in str(x).lower())
                        if not card:
                            card = link.find_parent('td')  # Sometimes in table
                        
                        if card:
                            # Extract from parent
                            title = link.get_text(strip=True)
                            
                            # Find company - might be in different places
                            company_elem = card.find('span', {'data-testid': 'company-name'}) or \
                                        card.find('a', {'data-testid': 'company-name'}) or \
                                        card.find('div', {'data-testid': 'company-name'})
                            
                            if not company_elem:
                                # Try finding by text content
                                company_elem = card.find('span', class_=lambda x: x and 'company' in str(x).lower())
                            
                            location_elem = card.find('div', {'data-testid': 'job-location'}) or \
                                        card.find('div', class_=lambda x: x and 'location' in str(x).lower())
                            
                            href = link.get('href', '')
                            if href and not href.startswith('http'):
                                href = f"https://nl.indeed.com{href}"
                            
                            if title:
                                jobs.append({
                                    'title': title,
                                    'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                                    'location': location_elem.get_text(strip=True) if location_elem else location,
                                    'url': href,
                                    'source': 'Indeed NL',
                                    'date_scraped': datetime.now().isoformat()
                                })
                                print(f"  ✓ {title}")
                                
                    except Exception as e:
                        continue
            else:
                # Process job cards if found
                print(f"  Found {len(job_cards)} job cards")
                for card in job_cards[:25]:
                    try:
                        title_elem = card.find('h2', class_='jobTitle') or \
                                card.find('a', {'data-testid': 'job-title'})
                        
                        company_elem = card.find('span', {'data-testid': 'company-name'}) or \
                                    card.find('a', {'data-testid': 'company-name'})
                        
                        location_elem = card.find('div', {'data-testid': 'job-location'})
                        
                        if title_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                                'location': location_elem.get_text(strip=True) if location_elem else location,
                                'url': f"https://nl.indeed.com{title_elem.get('href', '')}" if title_elem.get('href') else '',
                                'source': 'Indeed NL',
                                'date_scraped': datetime.now().isoformat()
                            })
                            
                    except Exception as e:
                        continue
            
            if jobs:
                print(f"  ✅ Successfully scraped {len(jobs)} jobs from Indeed")
            else:
                print("  ⚠️  No jobs extracted - trying alternative method...")
                # Last resort: use regex to find job data
                import re
                pattern = r'"jobTitle":"([^"]+)".*?"companyName":"([^"]+)"'
                matches = re.findall(pattern, response.text)
                for title, company in matches[:10]:
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': url,
                        'source': 'Indeed NL (regex)',
                        'date_scraped': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title} at {company}")
            
            return jobs
            
        except Exception as e:
            print(f"  ❌ Indeed scraping failed: {e}")
            return []    
    def save_jobs(self, jobs, filename="jobs_found.json"):
        """Save jobs to JSON file"""
        with open(filename, 'w') as f:
            json.dump(jobs, f, indent=2)
        print(f"\n💾 Saved {len(jobs)} jobs to {filename}")
    
    def test_scrapers(self):
        """Test both scrapers to see what we get"""
        print("="*50)
        print("TESTING JOB SCRAPERS FOR NETHERLANDS")
        print("="*50)
        
        all_jobs = []
        
        # Test LinkedIn
        linkedin_jobs = self.get_linkedin_public(
            query="software engineer",  # Broader search first
            location="Netherlands"
        )
        all_jobs.extend(linkedin_jobs)
        
        # Test Indeed
        indeed_jobs = self.get_indeed_nl(
            query="software engineer",
            location="Netherlands"
        )
        all_jobs.extend(indeed_jobs)
        
        # Save results
        self.save_jobs(all_jobs)
        
        print("\n" + "="*50)
        print(f"TOTAL JOBS FOUND: {len(all_jobs)}")
        print(f"- LinkedIn: {len(linkedin_jobs)}")
        print(f"- Indeed NL: {len(indeed_jobs)}")
        print("="*50)
        
        return all_jobs

if __name__ == "__main__":
    scraper = JobScraper()
    jobs = scraper.test_scrapers()