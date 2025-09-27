#!/usr/bin/env python3
"""Add Selenium description fetching to analyzer_ai.py"""

# Read current analyzer
with open('analyzer_ai.py', 'r') as f:
    current = f.read()

# Selenium imports to add
selenium_imports = '''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
'''

# Add imports after datetime
pos = current.find('from datetime import datetime') + len('from datetime import datetime')
current = current[:pos] + selenium_imports + current[pos:]

# Methods to add after __init__
selenium_methods = '''
    
    def setup_driver(self):
        """Setup Chrome driver for fetching job descriptions"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print('Selenium driver initialized')
        except Exception as e:
            print(f'Warning: Could not setup driver: {e}')
            self.driver = None
            self.wait = None
    
    def get_job_description(self, url):
        """Fetch full job description from LinkedIn"""
        if not self.driver:
            return ""
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # Try clicking see more
            selectors = [
                "button[aria-label='Click to see more description']",
                "button.see-more-less-html__button"
            ]
            
            for sel in selectors:
                try:
                    btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                    btn.click()
                    time.sleep(1)
                    break
                except:
                    pass
            
            # Get description
            desc_selectors = [
                "div.show-more-less-html__markup",
                "div.jobs-description__content"
            ]
            
            for sel in desc_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                    return elem.text
                except:
                    pass
            
            return ""
        except Exception as e:
            return ""
'''

# Add after __init__ 
init_end = current.find('print(\'AI Analyzer initialized with Claude API\')')
insert_pos = current.find('\n', init_end) + 1
insert_pos = current.find('\n', insert_pos) + 1  # Next line

current = current[:insert_pos] + '\n        # Setup Selenium\n        self.setup_driver()' + selenium_methods + current[insert_pos:]

# Update analyze_job_fit to fetch descriptions
old_line = 'description = job_data.get(\'description\', \'\')'
new_lines = '''description = job_data.get('description', '')
        
        # Fetch description if empty
        if not description or len(description) < 50:
            print('  Fetching description...')
            description = self.get_job_description(job_data.get('url', ''))
            if description:
                print(f'  Got {len(description)} chars')
                job_data['description'] = description'''

current = current.replace(old_line, new_lines)

# Write updated analyzer
with open('analyzer_ai.py', 'w') as f:
    f.write(current)

print('Updated analyzer_ai.py with Selenium')
print('Changes:')
print('  - Added Selenium imports')
print('  - Added setup_driver() method')
print('  - Added get_job_description() method')
print('  - Modified analyze_job_fit to fetch descriptions')
