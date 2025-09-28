# job_analyzer_working.py - This WILL work
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import re

class JobAnalyzer:
    def __init__(self, profile_path='yigit_profile.json'):
        with open(profile_path) as f:
            self.profile = json.load(f)
        
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.load_cookies()
    
    def expand_description(self):
        """Click the EXACT See More button using the selectors from your screenshot"""
        expanded = False
        
        # Method 1: Using the exact aria-label
        try:
            button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Click to see more description"]'))
            )
            button.click()
            expanded = True
            print("    ✓ Expanded via aria-label")
            time.sleep(1)
            return True
        except:
            pass
        
        # Method 2: Using the specific class combination
        if not expanded:
            try:
                button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'button.jobs-description__footer-button'
                )
                button.click()
                expanded = True
                print("    ✓ Expanded via class")
                time.sleep(1)
                return True
            except:
                pass
        
        # Method 3: Find span with "See more" text and click parent
        if not expanded:
            try:
                span = self.driver.find_element(
                    By.XPATH, 
                    '//span[@class="artdeco-button__text" and text()="See more"]'
                )
                button = span.find_element(By.XPATH, '..')  # Get parent button
                button.click()
                expanded = True
                print("    ✓ Expanded via text span")
                time.sleep(1)
                return True
            except:
                pass
        
        # Method 4: Using aria-expanded attribute
        if not expanded:
            try:
                button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'button[aria-expanded="false"][aria-label*="see more"]'
                )
                self.driver.execute_script("arguments[0].click();", button)
                expanded = True
                print("    ✓ Expanded via JavaScript")
                time.sleep(1)
                return True
            except:
                pass
        
        return False
    
    def deep_analyze_linkedin(self, job):
        """Get FULL job description"""
        try:
            self.driver.get(job['url'])
            time.sleep(2)
            
            # Get initial description length
            initial_desc = ""
            try:
                initial_desc = self.driver.find_element(By.CLASS_NAME, "jobs-description__content").text
            except:
                pass
            
            # Expand the description
            expanded = self.expand_description()
            
            # Get full description
            full_description = ""
            try:
                # After expanding, get the full content
                desc_element = self.driver.find_element(By.CLASS_NAME, "jobs-description__content")
                full_description = desc_element.text
                
                if expanded and len(full_description) > len(initial_desc):
                    print(f"    ✓ Got FULL description ({len(full_description)} chars vs initial {len(initial_desc)})")
                elif not expanded:
                    print(f"    ⚠️ Using partial description ({len(full_description)} chars)")
            except Exception as e:
                print(f"    ❌ Error getting description: {e}")
            
            # Extract other details
            details = {
                'description': full_description,
                'applicants': self.safe_extract(".jobs-unified-top-card__applicant-count"),
                'seniority': self.safe_extract(".jobs-unified-top-card__job-insight"),
                'posted': self.safe_extract(".jobs-unified-top-card__posted-date")
            }
            
            # Extract requirements from full description
            requirements = self.extract_requirements(full_description)
            
            # Calculate match
            match_score = self.calculate_match(requirements)
            
            return {
                'score': match_score['total'],
                'type': 'deep',
                'expanded': expanded,
                'description_length': len(full_description),
                'details': details,
                'requirements': requirements,
                'match_details': match_score,
                'recommendation': self.get_recommendation(match_score['total'])
            }
            
        except Exception as e:
            print(f"    ❌ Analysis failed: {e}")
            return self.quick_score(job)
    
    def extract_requirements(self, description):
        """Extract requirements from description"""
        if not description or len(description) < 100:
            return {'skills': [], 'experience_years': None, 'languages': [], 'education': []}
        
        desc_lower = description.lower()
        requirements = {
            'skills': [],
            'experience_years': None,
            'languages': [],
            'education': []
        }
        
        # Technical skills
        tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node', 'nodejs', 'sql', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'git', 'c#', '.net', 'asp.net', 'c++', 'php', 'ruby', 'go', 'rust',
            'machine learning', 'ai', 'ml', 'pytorch', 'tensorflow', 'deep learning'
        ]
        
        for skill in tech_skills:
            if skill in desc_lower:
                requirements['skills'].append(skill)
        
        # Experience
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'minimaal\s+(\d+)\s+jaar',
            r'ten minste\s+(\d+)\s+jaar',
            r'(\d+)\s+jaar\s+ervaring'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                requirements['experience_years'] = int(match.group(1))
                break
        
        # Languages
        if 'fluent dutch' in desc_lower or 'vloeiend nederlands' in desc_lower:
            requirements['languages'].append('Dutch (Fluent)')
        elif 'dutch' in desc_lower or 'nederlands' in desc_lower:
            requirements['languages'].append('Dutch')
        
        # Education
        if 'bachelor' in desc_lower or 'bsc' in desc_lower or 'hbo' in desc_lower:
            requirements['education'].append('Bachelor')
        if 'master' in desc_lower or 'msc' in desc_lower or 'wo' in desc_lower:
            requirements['education'].append('Master')
        
        return requirements
    
    def calculate_match(self, requirements):
        """Calculate match score based on requirements"""
        scores = {
            'skills': 60,
            'experience': 70,
            'education': 100,
            'languages': 100,
            'total': 0
        }
        
        # Skills matching
        if requirements['skills']:
            your_skills = ['python', 'java', 'javascript', 'react', 'sql', 'docker', 
                          'git', 'machine learning', 'ai', 'ml', 'pytorch', 'c++']
            matched = sum(1 for s in requirements['skills'] if s in your_skills)
            scores['skills'] = (matched / len(requirements['skills']) * 100) if requirements['skills'] else 60
        
        # Experience matching
        if requirements['experience_years'] is not None:
            years = requirements['experience_years']
            if years == 0:
                scores['experience'] = 100
            elif years <= 1:
                scores['experience'] = 85
            elif years <= 2:
                scores['experience'] = 65
            elif years <= 3:
                scores['experience'] = 45
            else:
                scores['experience'] = 25
        
        # Language matching
        if requirements['languages']:
            if 'Dutch (Fluent)' in requirements['languages']:
                scores['languages'] = 30  # You have A2
            elif 'Dutch' in requirements['languages']:
                scores['languages'] = 50
        
        # Calculate total
        scores['total'] = (
            scores['skills'] * 0.35 +
            scores['experience'] * 0.30 +
            scores['education'] * 0.20 +
            scores['languages'] * 0.15
        )
        
        return scores
    
    def quick_score(self, job):
        """Quick fallback scoring"""
        score = 50
        title = job['title'].lower()
        
        if any(w in title for w in ['junior', 'graduate', 'entry']):
            score += 25
        if any(w in title for w in ['senior', 'lead', 'principal']):
            score -= 30
        if any(w in title for w in ['ai', 'ml', 'machine learning']):
            score += 15
        
        return {
            'score': min(max(score, 0), 100),
            'type': 'quick',
            'recommendation': self.get_recommendation(score)
        }
    
    def safe_extract(self, selector):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return ""
    
    def get_recommendation(self, score):
        if score >= 75:
            return "🟢 APPLY TODAY"
        elif score >= 60:
            return "🟡 Apply this week"
        elif score >= 45:
            return "🟠 Consider"
        else:
            return "🔴 Skip"
    
    def load_cookies(self):
        try:
            self.driver.get("https://linkedin.com")
            with open('linkedin_cookies.pkl', 'rb') as f:
                for cookie in pickle.load(f):
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
            print("✅ Cookies loaded")
        except:
            print("Login to LinkedIn...")
            input("Press Enter when ready...")
    
    def analyze_all_jobs(self, jobs_file='jobs_found.json'):
        with open(jobs_file) as f:
            jobs = json.load(f)
        
        print(f"📊 Analyzing {len(jobs)} jobs...")
        analyzed = []
        
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] {job['title'][:40]}...")
            
            if 'linkedin' in job.get('url', '').lower() and job.get('url'):
                job['analysis'] = self.deep_analyze_linkedin(job)
            else:
                job['analysis'] = self.quick_score(job)
            
            analyzed.append(job)
            
            # Save progress
            if i % 5 == 0:
                with open('progress.json', 'w') as f:
                    json.dump(analyzed, f)
        
        # Sort and save
        analyzed.sort(key=lambda x: x['analysis']['score'], reverse=True)
        
        with open('analyzed_final.json', 'w') as f:
            json.dump(analyzed, f, indent=2)
        
        # Create action plan
        self.create_plan(analyzed)
        
        return analyzed
    
    def create_plan(self, jobs):
        high = [j for j in jobs if j['analysis']['score'] >= 75]
        good = [j for j in jobs if 60 <= j['analysis']['score'] < 75]
        
        with open('ACTION_PLAN.md', 'w') as f:
            f.write("# Job Application Priority\n\n")
            f.write(f"## 🟢 APPLY TODAY ({len(high)} jobs)\n")
            for j in high:
                f.write(f"- **{j['title']}** at {j['company']} ({j['analysis']['score']:.0f}%)\n")
                f.write(f"  - {j['url']}\n")
                if j['analysis'].get('expanded'):
                    f.write(f"  - ✅ Full description analyzed\n")
                if j['analysis'].get('requirements', {}).get('skills'):
                    f.write(f"  - Skills: {', '.join(j['analysis']['requirements']['skills'][:5])}\n")
            
            f.write(f"\n## 🟡 APPLY THIS WEEK ({len(good)} jobs)\n")
            for j in good[:10]:
                f.write(f"- {j['title']} at {j['company']} ({j['analysis']['score']:.0f}%)\n")
        
        print(f"\n✅ Analysis complete!")
        print(f"🟢 Apply today: {len(high)} jobs")
        print(f"🟡 Apply this week: {len(good)} jobs")

# Run it
if __name__ == "__main__":
    analyzer = JobAnalyzer()
    analyzer.analyze_all_jobs()