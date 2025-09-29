from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os

class ApplyLinkExtractor:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup_driver(self):
        """Initialize driver only when needed"""
        if self.driver:
            return
            
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Run in background
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Load cookies
        cookie_file = 'config/linkedin_cookies.pkl'
        if os.path.exists(cookie_file):
            self.driver.get("https://www.linkedin.com")
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
            self.driver.refresh()
    
    def get_apply_link(self, job_url):
        """Extract apply method - returns URL or 'EASY_APPLY'"""
        if not job_url:
            return None
        
        self.setup_driver()
        result = None  # Store result before cleanup
        
        try:
            self.driver.get(job_url)
            time.sleep(2)
            
            # Find apply buttons
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button.jobs-apply-button, div.jobs-apply-button--top-card button")
            
            for button in buttons:
                if not button.is_displayed():
                    continue
                
                aria_label = (button.get_attribute('aria-label') or '').lower()
                button_text = button.text or ''
                
                # Easy Apply
                if 'easy apply' in aria_label.lower() or 'Easy Apply' in button_text:
                    result = "EASY_APPLY"
                    break
                
                # External Apply
                elif 'on company website' in aria_label:
                    button.click()
                    time.sleep(2)
                    
                    # Check for new tab
                    if len(self.driver.window_handles) > 1:
                        original = self.driver.current_window_handle
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        result = self.driver.current_url
                        self.driver.close()
                        self.driver.switch_to.window(original)
                    else:
                        # Same tab redirect
                        current = self.driver.current_url
                        if 'linkedin.com' not in current:
                            result = current
                            self.driver.back()
                    break
                    
        except Exception as e:
            print(f"Error extracting apply link: {e}")
        finally:
            # Always close the driver after use
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
        
        return result
    
    def __del__(self):
        """Cleanup driver on deletion"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass