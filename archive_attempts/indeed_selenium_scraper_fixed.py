# indeed_selenium_scraper_fixed.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
from datetime import datetime

def scrape_indeed_with_selenium(query="software engineer", location="Amsterdam"):
    """Use Selenium to get Indeed jobs WITH working URLs"""
    print(f"🔍 Scraping Indeed with Selenium: {query} in {location}")
    
    # Simple options that were working before
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(f"https://nl.indeed.com/jobs?q={query}&l={location}")
        time.sleep(3)  # Let page load
        
        jobs = []
        
        # Find job cards - Indeed uses data-jk attribute for job keys
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-jk]')
        
        if not job_cards:
            # Try alternative selector
            job_cards = driver.find_elements(By.CSS_SELECTOR, '.job_seen_beacon')
        
        print(f"Found {len(job_cards)} job cards")
        
        for card in job_cards[:15]:
            try:
                # Get job key from card
                job_key = card.get_attribute('data-jk')
                if not job_key:
                    # Try finding it in child elements
                    jk_elem = card.find_element(By.CSS_SELECTOR, '[data-jk]')
                    job_key = jk_elem.get_attribute('data-jk')
                
                # Get title - FIXED SELECTOR
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, 'h2 a span[title]')
                    title = title_elem.get_attribute('title')
                except:
                    # Alternative selector if structure changed
                    title_elem = card.find_element(By.CSS_SELECTOR, 'h2 span[title]')
                    title = title_elem.get_attribute('title')
                
                # Get company
                try:
                    company = card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
                except:
                    company = "Unknown"
                
                # Get location
                try:
                    location_text = card.find_element(By.CSS_SELECTOR, '[data-testid="job-location"]').text
                except:
                    location_text = location
                
                # Build URL with job key
                job_url = f"https://nl.indeed.com/viewjob?jk={job_key}" if job_key else ""
                
                if title and job_url:
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'url': job_url,
                        'source': 'Indeed NL',
                        'date_scraped': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}... -> {job_url}")
                    
            except Exception as e:
                print(f"  ⚠️ Error on card: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Failed to load Indeed: {e}")
    
    finally:
        driver.quit()
    
    print(f"\n✅ Scraped {len(jobs)} Indeed jobs with URLs")
    return jobs

# THIS IS WHAT WAS MISSING - THE ACTUAL EXECUTION!
if __name__ == "__main__":
    jobs = scrape_indeed_with_selenium()
    
    if jobs:
        # Save to file
        with open('indeed_test.json', 'w') as f:
            json.dump(jobs, f, indent=2)
        
        print(f"\nFirst 3 jobs with URLs:")
        for job in jobs[:3]:
            print(f"  {job['title']}")
            print(f"  URL: {job['url']}\n")
    else:
        print("No jobs found - Indeed might be blocking")