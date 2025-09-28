import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import hashlib
import json

class ValidatedEnricher:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        
    def fetch_with_validation(self, job_url):
        """Fetch description with quality checks"""
        result = {
            'description': '',
            'language': 'unknown',
            'quality_score': 0,
            'requirements_found': False,
            'degree_requirement': None,
            'experience_years': None,
            'fetched_sections': []
        }
        
        try:
            self.driver.get(job_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Click all "show more" buttons
            self._expand_all_sections()
            
            # Fetch from multiple selectors to ensure completeness
            description_parts = []
            selectors = [
                "div.jobs-description__content",
                "div.description__text",
                "section.jobs-box__html-content",
                "div.show-more-less-html__markup",
                "div[class*='description']",
                "section[class*='description']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and text not in description_parts:
                            description_parts.append(text)
                            result['fetched_sections'].append(selector)
                except:
                    continue
            
            full_description = "\n\n".join(description_parts)
            result['description'] = full_description
            
            # Detect language
            result['language'] = self._detect_language(full_description)
            
            # Extract requirements
            result['degree_requirement'] = self._extract_degree_requirement(full_description)
            result['experience_years'] = self._extract_experience_years(full_description)
            
            # Quality validation
            result['quality_score'] = self._calculate_quality_score(full_description)
            result['requirements_found'] = bool(re.search(
                r'(requirements?|qualifications?|must have|required|vereisten|eisen)',
                full_description, re.IGNORECASE
            ))
            
            # Log if quality is poor
            if result['quality_score'] < 50:
                print(f"⚠️ Low quality description fetched: {result['quality_score']}%")
                print(f"  Sections found: {result['fetched_sections']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Enrichment failed: {e}")
            result['error'] = str(e)
            return result
    
    def _expand_all_sections(self):
        """Click all expandable sections"""
        expand_buttons = [
            "button[aria-label*='Show more']",
            "button[aria-label*='See more']",
            "button.show-more-less-html__button",
            "button[class*='show-more']",
            "button[data-tracking-control-name*='show-more']"
        ]
        
        for selector in expand_buttons:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(0.5)
            except:
                continue
    
    def _detect_language(self, text):
        """Detect primary language of text"""
        dutch_words = ['een', 'van', 'het', 'de', 'en', 'is', 'voor', 'met', 'aan', 'bij']
        dutch_count = sum(1 for word in dutch_words if word in text.lower().split())
        
        if dutch_count > 10:
            return 'dutch'
        elif dutch_count > 3:
            return 'mixed'
        return 'english'
    
    def _extract_degree_requirement(self, text):
        """Extract degree requirements from text"""
        patterns = {
            'phd': r"(phd|doctorate|doctoral)",
            'masters': r"(master'?s?|msc|ma\b|wo\b|masteropleiding)",
            'bachelors': r"(bachelor'?s?|bsc|ba\b|hbo|bacheloropleiding)"
        }
        
        text_lower = text.lower()
        
        # Check for explicit requirements
        for degree, pattern in patterns.items():
            if re.search(pattern, text_lower):
                # Check if it's actually required
                context = text_lower[max(0, text_lower.find(pattern) - 50):][:200]
                if any(req in context for req in ['required', 'must', 'need', 'afgeronde', 'vereist']):
                    return degree
        
        return None
    
    def _extract_experience_years(self, text):
        """Extract years of experience requirement"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'minimaal\s+(\d+)\s+jaar',
            r'at\s+least\s+(\d+)\s+years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _calculate_quality_score(self, text):
        """Calculate description quality score"""
        score = 0
        
        # Length check
        if len(text) > 2000: score += 30
        elif len(text) > 1000: score += 20
        elif len(text) > 500: score += 10
        
        # Section checks
        sections = ['requirements', 'responsibilities', 'qualifications', 'about']
        for section in sections:
            if section in text.lower():
                score += 10
        
        # Structured content check
        if text.count('\n') > 5: score += 10
        if text.count('•') > 2 or text.count('-') > 5: score += 10
        if re.search(r'\d+\..*\n.*\d+\.', text): score += 10
        
        return min(score, 100)