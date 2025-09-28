#!/usr/bin/env python3
"""Enriches job data by fetching full descriptions from LinkedIn"""

import json
import time
import pickle
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class DescriptionEnricher:
    def __init__(self, cookies_path='config/linkedin_cookies.pkl'):
        self.cookies_path = cookies_path
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome with LinkedIn cookies"""
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Load LinkedIn and add cookies
        self.driver.get("https://www.linkedin.com")
        
        # Load cookies if they exist
        if Path(self.cookies_path).exists():
            with open(self.cookies_path, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
            self.driver.refresh()
            time.sleep(2)
    
    def fetch_description(self, job_url):
        """Fetch full description for a single job"""
        try:
            self.driver.get(job_url)
            time.sleep(2)
            
            # Try to click "See more" button
            see_more_selectors = [
                "button[aria-label*='more']",
                "button.see-more-less-html__button",
                "button.show-more-less-html__button"
            ]
            
            for selector in see_more_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    button.click()
                    time.sleep(1)
                    break
                except:
                    continue
            
            # Get description
            desc_selectors = [
                "div.show-more-less-html__markup",
                "div.jobs-description__content",
                "div.description__text"
            ]
            
            for selector in desc_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return elem.text
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error fetching {job_url}: {e}")
            return None
    
    def enrich_jobs(self, jobs_file):
        """Add descriptions to all jobs in a file"""
        # Load jobs
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
        
        print(f"Enriching {len(jobs)} jobs with descriptions...")
        
        # Setup driver
        self.setup_driver()
        
        enriched = []
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] {job['title'][:50]}...")
            
            if job.get('description'):
                print("  Already has description, skipping")
                enriched.append(job)
                continue
            
            desc = self.fetch_description(job['url'])
            if desc:
                job['description'] = desc
                print(f"  ✓ Got {len(desc)} chars")
            else:
                job['description'] = ""
                print("  ✗ No description found")
            
            enriched.append(job)
            time.sleep(2)  # Rate limit
        
        # Save enriched data
        output_file = jobs_file.replace('.json', '_enriched.json')
        with open(output_file, 'w') as f:
            json.dump(enriched, f, indent=2)
        
        print(f"\n✓ Saved enriched jobs to {output_file}")
        
        if self.driver:
            self.driver.quit()
        
        return enriched

if __name__ == '__main__':
    enricher = DescriptionEnricher()
    enricher.enrich_jobs('data/linkedin_jobs_20250927_134329.json')
