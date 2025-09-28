# linkedin_helper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pickle

class LinkedInHelper:
    def __init__(self):
        # Chrome options for better control
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def login_manual(self):
        
        """You login manually - safer than automation"""
        print("🔐 Opening LinkedIn for manual login...")
        self.driver.get("https://linkedin.com")
        print("\n⚠️  IMPORTANT:")
        print("1. Login to your LinkedIn account")
        print("2. Navigate to Jobs section")  # ADD THIS
        print("3. DO NOT CLOSE THE BROWSER!")  # ADD THIS
        input("\nPress Enter when you're logged in and ready...")
        
        # Save cookies for future use
        cookies = self.driver.get_cookies()
        with open('linkedin_cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        print("✅ Login successful! Cookies saved.")
    
    def load_cookies(self):
        """Try to load saved cookies"""
        try:
            with open('linkedin_cookies.pkl', 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            return True
        except:
            return False
    
    def search_jobs(self, query="AI engineer", location="Netherlands", easy_apply_only=True):
        """Search for jobs with filters"""
        print(f"\n🔍 Searching for: {query} in {location}")
        
        # Build search URL
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}"
        
        if easy_apply_only:
            search_url += "&f_AL=true"  # Easy Apply filter
        
        # Add more useful filters
        search_url += "&f_TPR=r86400"  # Posted in last 24 hours
        search_url += "&f_E=1,2"  # Entry level + Associate
        
        self.driver.get(search_url)
        time.sleep(3)  # Let page load
        
        print("📋 Current URL:", self.driver.current_url)
        return self.extract_job_listings()
    
    def extract_job_listings(self):
        """Extract job details from search results"""
        jobs = []
        
        try:
            # Wait for job cards to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card-container"))
            )
            
            # Find all job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
            print(f"Found {len(job_cards)} jobs")
            
            for i, card in enumerate(job_cards[:10], 1):  # First 10 jobs
                try:
                    card.click()
                    time.sleep(1)  # Wait for details to load
                    
                    # Extract job details
                    job = {
                        'title': self.safe_find_text(".job-details-jobs-unified-top-card__job-title"),
                        'company': self.safe_find_text(".job-details-jobs-unified-top-card__company-name"),
                        'location': self.safe_find_text(".job-details-jobs-unified-top-card__bullet"),
                        'has_easy_apply': self.check_easy_apply(),
                        'url': self.driver.current_url,
                        'index': i
                    }
                    
                    jobs.append(job)
                    print(f"  {i}. {'✅' if job['has_easy_apply'] else '❌'} {job['title']} at {job['company']}")
                    
                except Exception as e:
                    print(f"  ❌ Error extracting job {i}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error extracting jobs: {e}")
        
        return jobs
    
    def safe_find_text(self, selector):
        """Safely find and extract text"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return "N/A"
    
    def check_easy_apply(self):
        """Check if job has Easy Apply"""
        try:
            easy_apply = self.driver.find_element(
                By.XPATH, 
                "//button[contains(@aria-label, 'Easy Apply')]"
            )
            return True
        except:
            return False
    
    def prepare_application(self, job_url):
        """Navigate to job and prepare for application"""
        print(f"\n📝 Preparing application...")
        self.driver.get(job_url)
        time.sleep(2)
        
        # Check for Easy Apply button
        if self.check_easy_apply():
            print("✅ Easy Apply available!")
            print("\n⚠️  NEXT STEPS:")
            print("1. Review the job description")
            print("2. Click Easy Apply when ready")
            print("3. Fill any additional fields")
            print("4. Review before submitting")
            input("\nPress Enter when application is submitted...")
        else:
            print("❌ No Easy Apply - need to apply on company website")
    
    def cleanup(self):
        """Close the browser"""
        self.driver.quit()

# Test script
if __name__ == "__main__":
    helper = LinkedInHelper()
    
    try:
        # Login
        helper.login_manual()
        
        # Search for jobs
        jobs = helper.search_jobs(
            query="software engineer graduate",
            location="Netherlands",
            easy_apply_only=True
        )
        
        # Save jobs
        with open('linkedin_jobs.json', 'w') as f:
            json.dump(jobs, f, indent=2)
        
        print(f"\n💾 Saved {len(jobs)} jobs to linkedin_jobs.json")
        
        # Optional: Help apply to first Easy Apply job
        easy_apply_jobs = [j for j in jobs if j['has_easy_apply']]
        if easy_apply_jobs:
            print(f"\n🎯 Found {len(easy_apply_jobs)} Easy Apply jobs!")
            apply = input("Want to apply to the first one? (y/n): ")
            
            if apply.lower() == 'y':
                helper.prepare_application(easy_apply_jobs[0]['url'])
        
    finally:
        helper.cleanup()