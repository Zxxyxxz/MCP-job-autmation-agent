"""
LinkedIn Job Analyzer - Stable Version
Analyzes job descriptions and scores them based on profile match
"""

import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

class JobAnalyzer:
    def __init__(self, profile_path='../../yigit_profile.json', config_path='../config/settings.json'):
        # Load profile
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Setup Selenium
        self.setup_driver()
        
        # Setup logging
        logging.basicConfig(
            filename='../logs/analyzer.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Setup Chrome driver with optimized settings"""
        options = webdriver.ChromeOptions()
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f"--window-size={self.config['browser']['window_size']}")
        
        # Optional headless mode
        if self.config['browser'].get('headless'):
            options.add_argument('--headless')
        
        # User agent
        options.add_argument(f"user-agent={self.config['browser']['user_agent']}")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def analyze_jobs_file(self, jobs_file):
        """Analyze all jobs from a JSON file"""
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
        
        print(f"\n📊 Analyzing {len(jobs)} jobs from {jobs_file}")
        self.logger.info(f"Starting analysis of {len(jobs)} jobs")
        
        analyzed_jobs = []
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}] Analyzing: {job['title'][:50]}...")
            analyzed_job = self.analyze_single_job(job)
            analyzed_jobs.append(analyzed_job)
            
            # Rate limiting
            time.sleep(self.config['search_settings']['wait_between_requests'])
        
        # Sort by score
        analyzed_jobs.sort(key=lambda x: x['score'], reverse=True)
        
        # Save results
        self.save_analysis(analyzed_jobs)
        self.create_action_plan(analyzed_jobs)
        
        return analyzed_jobs
    
    def analyze_single_job(self, job):
        """Analyze a single job posting"""
        try:
            # Navigate to job URL
            self.driver.get(job['url'])
            time.sleep(2)
            
            # Try to expand description
            description = self.get_full_description()
            
            # Calculate score
            score_details = self.calculate_score(job, description)
            
            # Add analysis to job data
            job['description'] = description
            job['score'] = score_details['total']
            job['score_details'] = score_details
            job['analyzed_at'] = datetime.now().isoformat()
            
            print(f"  ✓ Score: {score_details['total']}/100")
            
            return job
            
        except Exception as e:
            self.logger.error(f"Failed to analyze job {job.get('job_id')}: {e}")
            print(f"  ❌ Failed to analyze: {e}")
            job['score'] = 0
            job['error'] = str(e)
            return job
    
    def get_full_description(self):
        """Get the full job description from LinkedIn"""
        description = ""
        
        try:
            # Try to click "See more" button
            see_more_selectors = [
                "button[aria-label='Click to see more description']",
                "button.jobs-description__see-more",
                "button.see-more-less-html__button",
                "button[data-tracking-control-name='public_jobs_show-more-html-btn']"
            ]
            
            for selector in see_more_selectors:
                try:
                    button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button.click()
                    print("    ✓ Expanded description")
                    time.sleep(1)
                    break
                except:
                    continue
            
            # Get description text
            description_selectors = [
                "div.jobs-description__content",
                "div.show-more-less-html__markup",
                "div.description__text",
                "section.jobs-description"
            ]
            
            for selector in description_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    description = elem.text
                    if description:
                        break
                except:
                    continue
            
            if not description:
                # Fallback: get any text from the page
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    description = body.text[:5000]  # Limit to 5000 chars
                except:
                    description = "Could not extract description"
            
            return description
            
        except Exception as e:
            self.logger.warning(f"Could not get full description: {e}")
            return description or "Description not available"
    
    def calculate_score(self, job, description):
        """Calculate job match score"""
        weights = self.config['scoring']['weights']
        scores = {
            'skills_match': 0,
            'experience_level': 0,
            'location': 0,
            'visa_sponsorship': 0,
            'total': 0
        }
        
        # Combine title and description for analysis
        full_text = f"{job.get('title', '')} {job.get('company', '')} {description}".lower()
        
        # 1. Skills matching (40%)
        matched_skills = []
        total_skills = len(self.profile['skills']['languages']) + \
                       len(self.profile['skills']['frameworks']) + \
                       len(self.profile['skills']['tools'])
        
        for skill in self.profile['skills']['languages']:
            if skill.lower() in full_text:
                matched_skills.append(skill)
        
        for framework in self.profile['skills']['frameworks']:
            if framework.lower() in full_text:
                matched_skills.append(framework)
        
        for tool in self.profile['skills']['tools']:
            if tool.lower() in full_text:
                matched_skills.append(tool)
        
        if total_skills > 0:
            scores['skills_match'] = (len(matched_skills) / total_skills) * 100 * weights['skills_match']
        
        # 2. Experience level (20%)
        junior_keywords = ['junior', 'graduate', 'entry', 'early career', '0-2 years', '0-3 years']
        senior_keywords = ['senior', 'lead', 'principal', '5+ years', '7+ years', '10+ years']
        
        is_junior_friendly = any(keyword in full_text for keyword in junior_keywords)
        has_senior_requirement = any(keyword in full_text for keyword in senior_keywords)
        
        if is_junior_friendly:
            scores['experience_level'] = 100 * weights['experience_level']
        elif not has_senior_requirement:
            scores['experience_level'] = 70 * weights['experience_level']
        else:
            scores['experience_level'] = 30 * weights['experience_level']
        
        # 3. Location (20%)
        netherlands_cities = ['amsterdam', 'rotterdam', 'the hague', 'utrecht', 'eindhoven', 
                            'enschede', 'netherlands', 'dutch', 'hybrid', 'remote']
        
        if any(city in job.get('location', '').lower() for city in netherlands_cities):
            scores['location'] = 100 * weights['location']
        elif 'remote' in full_text:
            scores['location'] = 80 * weights['location']
        else:
            scores['location'] = 40 * weights['location']
        
        # 4. Visa sponsorship (20%)
        positive_visa = ['visa sponsorship', 'work permit', 'relocation', 'international candidates']
        negative_visa = ['no sponsorship', 'eu only', 'must have right to work', 'citizens only']
        
        has_positive = any(term in full_text for term in positive_visa)
        has_negative = any(term in full_text for term in negative_visa)
        
        if has_positive:
            scores['visa_sponsorship'] = 100 * weights['visa_sponsorship']
        elif has_negative:
            scores['visa_sponsorship'] = 0
        else:
            scores['visa_sponsorship'] = 50 * weights['visa_sponsorship']  # Neutral
        
        # Calculate total
        scores['total'] = round(sum([scores[k] for k in weights.keys()]))
        scores['matched_skills'] = matched_skills
        
        return scores
    
    def save_analysis(self, analyzed_jobs):
        """Save analyzed jobs to JSON"""
        filename = f"../data/analyzed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(analyzed_jobs, f, indent=2)
        
        print(f"\n💾 Saved analysis to {filename}")
        self.logger.info(f"Saved analysis to {filename}")
    
    def create_action_plan(self, analyzed_jobs):
        """Create a prioritized action plan"""
        min_score = self.config['scoring']['minimum_score']
        auto_score = self.config['scoring']['auto_apply_score']
        
        high_priority = [j for j in analyzed_jobs if j['score'] >= auto_score]
        medium_priority = [j for j in analyzed_jobs if min_score <= j['score'] < auto_score]
        
        plan = []
        plan.append(f"# Job Application Action Plan - {datetime.now().strftime('%Y-%m-%d')}\n")
        plan.append(f"\n## Summary")
        plan.append(f"- Total jobs analyzed: {len(analyzed_jobs)}")
        plan.append(f"- High priority (score >= {auto_score}): {len(high_priority)}")
        plan.append(f"- Medium priority (score >= {min_score}): {len(medium_priority)}\n")
        
        plan.append(f"\n## 🎯 HIGH PRIORITY - Apply Immediately\n")
        for i, job in enumerate(high_priority[:10], 1):
            plan.append(f"\n### {i}. {job['title']} at {job['company']}")
            plan.append(f"- **Score**: {job['score']}/100")
            plan.append(f"- **Location**: {job.get('location', 'Unknown')}")
            plan.append(f"- **URL**: {job['url']}")
            if job.get('score_details', {}).get('matched_skills'):
                plan.append(f"- **Matched Skills**: {', '.join(job['score_details']['matched_skills'][:5])}")
            plan.append("")
        
        plan.append(f"\n## 📋 MEDIUM PRIORITY - Review & Apply\n")
        for i, job in enumerate(medium_priority[:10], 1):
            plan.append(f"\n### {i}. {job['title']} at {job['company']}")
            plan.append(f"- **Score**: {job['score']}/100")
            plan.append(f"- **URL**: {job['url']}")
            plan.append("")
        
        filename = f"../data/ACTION_PLAN_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, 'w') as f:
            f.write('\n'.join(plan))
        
        print(f"\n📋 Created action plan: {filename}")
        self.logger.info(f"Created action plan: {filename}")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'driver'):
            self.driver.quit()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        jobs_file = sys.argv[1]
    else:
        # Find the most recent jobs file
        import glob
        import os
        
        files = glob.glob('../data/linkedin_jobs_*.json')
        if files:
            jobs_file = max(files, key=os.path.getctime)
        else:
            print("No jobs file found. Run the scraper first.")
            sys.exit(1)
    
    analyzer = JobAnalyzer()
    analyzer.analyze_jobs_file(jobs_file)
