import requests
from bs4 import BeautifulSoup
from datetime import datetime

class LinkedInScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def scrape_jobs(self, search_term, location):
        return self.get_linkedin_public(search_term, location)
    
    def get_linkedin_public(self, query, location):
        jobs = []
        url = f'https://www.linkedin.com/jobs/search?keywords={query}&location={location}'
        
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', {'class': 'base-card'})[:20]
            
            for card in job_cards:
                try:
                    title_elem = card.find('h3', {'class': 'base-search-card__title'})
                    company_elem = card.find('h4', {'class': 'base-search-card__subtitle'})
                    location_elem = card.find('span', {'class': 'job-search-card__location'})
                    link_elem = card.find('a', {'class': 'base-card__full-link'})
                    
                    if title_elem and company_elem and link_elem:
                        job = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip(),
                            'location': location_elem.text.strip() if location_elem else location,
                            'url': link_elem.get('href', ''),
                            'description': '',
                            'source': 'linkedin',
                            'scraped_at': datetime.now().isoformat()
                        }
                        jobs.append(job)
                except:
                    continue
                    
        except Exception as e:
            print(f'Scraping error: {e}')
            
        return jobs