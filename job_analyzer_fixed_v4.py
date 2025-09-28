# job_analyzer_v4.py - COMPLETE FIX with Indeed support
import json
import time
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import re
from datetime import datetime

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
        """Click See More button for LinkedIn"""
        try:
            button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Click to see more description"]'))
            )
            button.click()
            print("    ✓ Expanded description")
            time.sleep(1)
            return True
        except:
            return False
    
    def deep_analyze_linkedin(self, job):
        """Analyze LinkedIn job with full description"""
        try:
            self.driver.get(job['url'])
            time.sleep(2)
            
            # Expand and get description
            self.expand_description()
            
            full_description = ""
            try:
                desc_element = self.driver.find_element(By.CLASS_NAME, "jobs-description__content")
                full_description = desc_element.text
                print(f"    ✓ Got {len(full_description)} chars")
            except:
                print(f"    ⚠️ No description found")
            
            # Extract requirements and calculate match
            requirements = self.extract_requirements(full_description)
            match_score = self.calculate_match(requirements)
            
            return {
                'score': match_score['total'],
                'type': 'linkedin_deep',
                'description_length': len(full_description),
                'description': full_description[:500] + "..." if len(full_description) > 500 else full_description,
                'requirements': requirements,
                'match_details': match_score,
                'recommendation': self.get_recommendation(match_score['total'])
            }
            
        except Exception as e:
            print(f"    ❌ LinkedIn analysis failed: {e}")
            return self.quick_score(job)
    
    def deep_analyze_indeed(self, job):
        """Analyze Indeed job (Dutch content)"""
        try:
            self.driver.get(job['url'])
            time.sleep(2)
            
            full_description = ""
            try:
                # Indeed uses different selectors
                desc_element = self.driver.find_element(By.ID, "jobDescriptionText")
                full_description = desc_element.text
                print(f"    ✓ Got Indeed description: {len(full_description)} chars")
            except:
                try:
                    # Alternative selector
                    desc_element = self.driver.find_element(By.CLASS_NAME, "jobsearch-jobDescriptionText")
                    full_description = desc_element.text
                except:
                    print(f"    ⚠️ No Indeed description found")
            
            # Check if Dutch and needs translation
            if self.is_dutch(full_description):
                print(f"    📝 Dutch content detected - analyzing keywords only")
                # For now, do basic keyword matching
                # Later: Add translation API
            
            requirements = self.extract_requirements(full_description)
            match_score = self.calculate_match(requirements)
            
            return {
                'score': match_score['total'],
                'type': 'indeed_deep',
                'description_length': len(full_description),
                'description': full_description[:500] + "..." if len(full_description) > 500 else full_description,  # ADD THIS LINE!
                'is_dutch': self.is_dutch(full_description),
                'requirements': requirements,
                'match_details': match_score,
                'recommendation': self.get_recommendation(match_score['total'])
            }
            
        except Exception as e:
            print(f"    ❌ Indeed analysis failed: {e}")
            return self.quick_score(job)
    
    def is_dutch(self, text):
        """Check if text is Dutch"""
        dutch_words = ['de', 'het', 'een', 'van', 'en', 'met', 'voor', 'bij', 'als', 'wij', 'jij', 'onze']
        text_lower = text.lower()
        dutch_count = sum(1 for word in dutch_words if word in text_lower.split())
        return dutch_count > 5
    
    def extract_requirements(self, description):
        """Extract requirements from job description"""
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
        
        # Experience patterns (English and Dutch)
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'minimaal\s+(\d+)\s+jaar',
            r'(\d+)\s+jaar\s+ervaring'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                requirements['experience_years'] = int(match.group(1))
                break
        
        # Language requirements
        if 'fluent dutch' in desc_lower or 'vloeiend nederlands' in desc_lower:
            requirements['languages'].append('Dutch (Fluent)')
        elif 'dutch' in desc_lower or 'nederlands' in desc_lower:
            requirements['languages'].append('Dutch')
        
        # Education
        if any(word in desc_lower for word in ['bachelor', 'bsc', 'hbo']):
            requirements['education'].append('Bachelor')
        if any(word in desc_lower for word in ['master', 'msc', 'wo']):
            requirements['education'].append('Master')
        
        return requirements
    
    def calculate_match(self, requirements):
        """Calculate match score"""
        scores = {
            'skills': 60,
            'experience': 70,
            'education': 100,
            'languages': 100,
            'total': 0
        }
        
        # Your skills
        your_skills = ['python', 'java', 'javascript', 'react', 'sql', 'docker', 
                      'git', 'machine learning', 'ai', 'ml', 'pytorch', 'c++']
        
        if requirements['skills']:
            matched = sum(1 for s in requirements['skills'] if s in your_skills)
            scores['skills'] = (matched / len(requirements['skills']) * 100) if requirements['skills'] else 60
        
        if requirements['experience_years'] is not None:
            years = requirements['experience_years']
            if years <= 1:
                scores['experience'] = 85
            elif years <= 2:
                scores['experience'] = 65
            elif years <= 3:
                scores['experience'] = 45
            else:
                scores['experience'] = 25
        
        if requirements['languages']:
            if 'Dutch (Fluent)' in requirements['languages']:
                scores['languages'] = 30
            elif 'Dutch' in requirements['languages']:
                scores['languages'] = 50
        
        scores['total'] = (
            scores['skills'] * 0.35 +
            scores['experience'] * 0.30 +
            scores['education'] * 0.20 +
            scores['languages'] * 0.15
        )
        
        return scores
    
    def quick_score(self, job):
        """Quick scoring based on title only"""
        score = 50
        title = job['title'].lower()
        
        if any(w in title for w in ['junior', 'intern', 'entry']):
            score += 25
        if any(w in title for w in ['senior', 'lead', 'principal']):
            score -= 30
        if any(w in title for w in ['ai', 'ml', 'machine learning', 'prosus']):
            score += 15
        
        return {
            'score': min(max(score, 0), 100),
            'type': 'quick',
            'recommendation': self.get_recommendation(score)
        }
    
    def get_recommendation(self, score):
        if score >= 75:
            return "🟢 APPLY TODAY"
        elif score >= 60:
            return "🟡 Apply this week"
        elif score >= 45:
            return "🟠 Consider"
        else:
            return "🔴 Skip"
    
    def safe_extract(self, selector):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return ""
    
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
            print("No cookies - will need to login")
    
    def analyze_all_jobs(self, jobs_file=None):
        """Analyze all jobs - auto-detect latest file"""
        # Auto-detect latest jobs file if not specified
        if jobs_file is None:
            job_files = glob.glob('jobs_*.json')
            if job_files:
                jobs_file = sorted(job_files)[-1]
                print(f"📁 Using latest file: {jobs_file}")
            else:
                jobs_file = 'jobs_found.json'
        
        with open(jobs_file) as f:
            jobs = json.load(f)
        
        print(f"📊 Analyzing {len(jobs)} jobs...")
        print(f"  - LinkedIn: {sum(1 for j in jobs if j['source'] == 'LinkedIn')}")
        print(f"  - Indeed: {sum(1 for j in jobs if j['source'] == 'Indeed NL')}\n")
        
        analyzed = []
        
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] {job['title'][:40]}...")
            
            # Choose analysis method based on source
            if 'linkedin' in job.get('url', '').lower():
                job['analysis'] = self.deep_analyze_linkedin(job)
            elif 'indeed' in job.get('url', '').lower():
                job['analysis'] = self.deep_analyze_indeed(job)
            else:
                job['analysis'] = self.quick_score(job)
            
            analyzed.append(job)
        
        # Sort by score
        analyzed.sort(key=lambda x: x['analysis']['score'], reverse=True)
        
        # Save results with timestamp
        output_file = f"analyzed_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analyzed, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved analysis to {output_file}")
        
        # Create action plan
        self.create_plan(analyzed)
        
        # Close browser
        self.driver.quit()
        
        return analyzed
    
    def create_plan(self, jobs):
        """Create actionable plan"""
        high = [j for j in jobs if j['analysis']['score'] >= 75]
        good = [j for j in jobs if 60 <= j['analysis']['score'] < 75]
        
        filename = f"ACTION_PLAN_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Job Application Priority - {datetime.now().strftime('%B %d, %Y')}\n\n")
            
            f.write(f"## 🟢 APPLY TODAY ({len(high)} jobs)\n")
            for j in high[:10]:  # Top 10
                f.write(f"- **{j['title']}** at {j['company']} ({j['analysis']['score']:.0f}%)\n")
                f.write(f"  - {j['url']}\n")
                if j['analysis'].get('requirements', {}).get('skills'):
                    f.write(f"  - Skills: {', '.join(j['analysis']['requirements']['skills'][:5])}\n")
            
            f.write(f"\n## 🟡 APPLY THIS WEEK ({len(good)} jobs)\n")
            for j in good[:10]:
                f.write(f"- {j['title']} at {j['company']} ({j['analysis']['score']:.0f}%)\n")
        
        print(f"✅ Action plan saved to {filename}")
        print(f"🟢 Apply today: {len(high)} jobs")
        print(f"🟡 Apply this week: {len(good)} jobs")

# Run it
if __name__ == "__main__":
    analyzer = JobAnalyzer()
    analyzer.analyze_all_jobs()