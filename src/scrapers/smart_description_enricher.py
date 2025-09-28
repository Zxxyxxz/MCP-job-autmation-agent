#!/usr/bin/env python3
"""Smart enricher with retry logic and better extraction"""

import json
import time
import pickle
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SmartDescriptionEnricher:
    def __init__(self, cookies_path='config/linkedin_cookies.pkl'):
        self.cookies_path = cookies_path
        self.max_retries = 2
        
    def setup_driver(self, headless=False):
        """Setup with better options"""
        options = webdriver.ChromeOptions()
        
        # Keep window in foreground
        options.add_argument('--force-device-scale-factor=1')
        options.add_argument('--start-maximized')
        
        # Better anti-detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Add user agent
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        if headless:
            options.add_argument('--headless=new')
        
        driver = webdriver.Chrome(options=options)
        
        # Execute CDP commands to hide automation
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": driver.execute_script("return navigator.userAgent").replace("Headless", "")
        })
        
        # Load LinkedIn and add cookies if they exist
        driver.get("https://www.linkedin.com")
        
        if Path(self.cookies_path).exists():
            with open(self.cookies_path, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
            driver.refresh()
            time.sleep(2)
        
        return driver
    
    def fetch_with_retry(self, job_url, attempt=1):
        """Fetch with retry logic"""
        driver = self.setup_driver(headless=(attempt > 1))
        
        try:
            # Bring window to front
            driver.switch_to.window(driver.current_window_handle)
            
            driver.get(job_url)
            time.sleep(random.uniform(2, 4))
            
            # Multiple strategies to get description
            description = None
            
            # Strategy 1: Try clicking See More
            see_more_selectors = [
                "button[aria-label*='see more']",
                "button[aria-label*='See more']",
                "button.see-more-less-html__button--more",
                "//button[contains(text(), 'see more')]"
            ]
            
            for selector in see_more_selectors:
                try:
                    if selector.startswith('//'):
                        btn = driver.find_element(By.XPATH, selector)
                    else:
                        btn = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    
                    try:
                        btn.click()
                    except:
                        driver.execute_script("arguments[0].click();", btn)
                    
                    time.sleep(1)
                    break
                except:
                    continue
            
            # Strategy 2: Get description with fallback selectors
            desc_selectors = [
                "div.show-more-less-html__markup",
                "div.jobs-description__content",
                "section.show-more-less-html",
                "div[class*='description']"
            ]
            
            for selector in desc_selectors:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                    description = elem.text
                    if description and len(description) > 100:
                        break
                except:
                    continue
            
            # Strategy 3: If still no description, try getting all text
            if not description or len(description) < 200:
                try:
                    main = driver.find_element(By.CSS_SELECTOR, "main, div.jobs-details, div.jobs-home__details")
                    description = main.text
                except:
                    description = None
            
            driver.quit()
            
            # Validate description quality
            if description and len(description) > 500:
                return description
            elif attempt < self.max_retries:
                print(f"  Retry {attempt + 1}/{self.max_retries}")
                time.sleep(3)
                return self.fetch_with_retry(job_url, attempt + 1)
            
            return description or ""
            
        except Exception as e:
            driver.quit()
            if attempt < self.max_retries:
                return self.fetch_with_retry(job_url, attempt + 1)
            return ""
    def get_apply_link(self, job_url):
        """Extract the actual apply link from LinkedIn job page"""
        try:
            if not self.driver:
                self.setup_driver()
            
            self.driver.get(job_url)
            time.sleep(3)
            
            # Try to find the actual apply button and get its link
            apply_selectors = [
                # LinkedIn's apply button that opens external link
                "a.jobs-apply-button--top-card",
                "div.jobs-apply-button--top-card a",
                # The actual apply link in the modal
                "a[data-tracking-control-name='public_jobs_apply-link-offsite']",
                # Easy Apply or external apply
                "button[aria-label*='Easy Apply']",
                "a.apply-button-link"
            ]
            
            for selector in apply_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # If it's a link, get href
                    if elem.tag_name == 'a':
                        apply_url = elem.get_attribute('href')
                        if apply_url and apply_url != job_url:
                            return apply_url
                    
                    # If it's a button, click it to reveal the actual link
                    elif elem.tag_name == 'button':
                        elem.click()
                        time.sleep(2)
                        # Now look for the revealed apply link
                        actual_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='apply']")
                        if actual_link:
                            return actual_link.get_attribute('href')
                except:
                    continue
            
            # If we can't find apply link, return the company careers page
            try:
                company_elem = self.driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link")
                company_url = company_elem.get_attribute('href')
                if company_url:
                    return company_url + "/careers"
            except:
                pass
            
            return job_url  # Fallback to job URL
        except Exception as e:
            print(f"Error getting apply link: {e}")
            return job_url
        
    def get_apply_link(self, job_url):
        """Extract the actual apply link from LinkedIn job page"""
        try:
            if self.driver:
                self.driver.get(job_url)
                time.sleep(2)
                
                # Look for apply button/link
                apply_selectors = [
                    "a.jobs-apply-button--top-card",
                    "a[data-tracking-control-name='public_jobs_apply-link-offsite']",
                    "a.apply-button",
                    "a[aria-label*='Apply']"
                ]
                
                for selector in apply_selectors:
                    try:
                        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        apply_url = elem.get_attribute('href')
                        if apply_url:
                            return apply_url
                    except:
                        continue
                
                # If no apply link found, return the job URL itself
                return job_url
        except:
            return job_url

if __name__ == '__main__':
    enricher = SmartDescriptionEnricher()
    test_url = "https://nl.linkedin.com/jobs/view/python-developer-at-corsearch-4294348465"
    desc = enricher.fetch_with_retry(test_url)
    print(f"Got {len(desc)} chars" if desc else "Failed")
