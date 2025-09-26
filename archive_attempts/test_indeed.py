# test_indeed_fix.py - Run this to see if we get URLs
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def test_indeed_with_urls():
    """Test if we can get Indeed URLs"""
    url = "https://nl.indeed.com/jobs?q=software+engineer&l=Netherlands"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for job keys in the HTML
    import re
    job_keys = re.findall(r'data-jk="([a-f0-9]+)"', response.text)
    
    print(f"Found {len(job_keys)} job keys")
    
    jobs = []
    for jk in job_keys[:5]:  # Test with 5
        job_url = f"https://nl.indeed.com/viewjob?jk={jk}"
        print(f"Job URL: {job_url}")
        jobs.append({'url': job_url})
    
    return jobs

# Run test
test_indeed_with_urls()