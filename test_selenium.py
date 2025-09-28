#!/usr/bin/env python3
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load jobs
with open('jobs_found.json', 'r') as f:
    jobs = json.load(f)

# Find LinkedIn job
linkedin_job = next((j for j in jobs if j.get('url') and 'linkedin' in j.get('url', '')), None)

if not linkedin_job:
    print('No LinkedIn jobs to test')
    exit()

print(f'Testing: {linkedin_job.get("title", "Unknown")}')
print(f'URL: {linkedin_job["url"]}')
print(f'Current desc length: {len(linkedin_job.get("description", ""))}')

# Setup driver
print('\nSetting up Chrome...')
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Fetch page
print(f'Fetching: {linkedin_job["url"]}')
driver.get(linkedin_job['url'])
time.sleep(3)

# Try clicking see more
for selector in ["button[aria-label='Click to see more description']", "button.see-more-less-html__button"]:
    try:
        btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()
        print('Expanded description')
        time.sleep(1)
        break
    except:
        pass

# Get description
description = None
for selector in ["div.show-more-less-html__markup", "div.jobs-description__content"]:
    try:
        elem = driver.find_element(By.CSS_SELECTOR, selector)
        description = elem.text
        if description:
            break
    except:
        pass

if description:
    print(f'\nSuccess: Retrieved {len(description)} chars')
    print(f'First 300 chars:\n{description[:300]}')
else:
    print('\nFailed to retrieve description')

driver.quit()
