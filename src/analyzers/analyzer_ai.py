"""AI-Powered Job Analyzer using Claude API
Provides intelligent job matching and cover letter generation"""

import json
import os
import re
from typing import Dict, Optional, Tuple
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print('⚠️  Warning: anthropic package not installed. Run: pip install anthropic')


class AIJobAnalyzer:
    """Use Claude to analyze job fit and generate application materials"""
    
    def __init__(self, api_key: Optional[str] = None, profile_path: str = 'config/yigit_profile.json'):
        """Initialize analyzer with Claude API"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError('anthropic package not installed. Install with: pip install anthropic')
        
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                'Anthropic API key required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.\\n'
                'Get your key at: https://console.anthropic.com/'
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Load candidate profile
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)

        print('✅ AI Analyzer initialized with Claude API access to profile data established.')

    def analyze_job_fit(self, job_data: Dict) -> Dict:
        """Analyze how well a job matches the candidate profile"""
        
        job_title = job_data.get('title', 'Unknown')
        company = job_data.get('company', 'Unknown')
        description = job_data.get('description', '')
        
        print(f'\\n🤖 Analyzing: {job_title} at {company}...')
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(job_data)
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model='claude-3-5-sonnet-20241022',
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent analysis
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            # Parse the response
            analysis = self._parse_analysis_response(response.content[0].text)
            
            print(f'  ✓ Score: {analysis["score"]}/100')
            print(f'  ✓ Recommendation: {analysis["recommendation"][:60]}...')
            
            return analysis
            
        except Exception as e:
            print(f'  ❌ Error analyzing job: {e}')
            return self._get_fallback_analysis()
    
    def _create_analysis_prompt(self, job_data: Dict) -> str:
        """Create a detailed prompt for job analysis"""
        
        return f"""You are an expert career advisor analyzing a job opportunity for Yigit Bezek.

        JOB DETAILS:
        Title: {job_data.get('title', 'N/A')}
        Company: {job_data.get('company', 'N/A')}
        Location: {job_data.get('location', 'N/A')}
        Description:
        {job_data.get('description', 'No description available')[:2000]}

        CANDIDATE PROFILE:
        {json.dumps(self.profile, indent=2)[:3000]}

        TASK:
        Analyze this job opportunity and provide:

        1. MATCH SCORE (0-100): How well does this role fit Yigit's profile?
        Consider: skills match, experience level, career trajectory, location, visa status

        2. KEY STRENGTHS (3-5 points): What makes Yigit a strong candidate?
        Be specific - reference his thesis, projects, or experience

        3. POTENTIAL CONCERNS (2-3 points): What might be challenging or mismatched?
        Consider: experience requirements, location, visa sponsorship needs

        4. FIT ASSESSMENT: Why is/isn't this a good opportunity?
        1-2 sentences explaining the overall fit

        5. APPLICATION STRATEGY: How should Yigit approach this application?
        Should he apply? What should he emphasize? Any concerns to address?

        FORMAT YOUR RESPONSE EXACTLY AS:
        SCORE: [number 0-100]
        STRENGTHS:
        - [strength 1]
        - [strength 2]
        - [strength 3]
        CONCERNS:
        - [concern 1]
        - [concern 2]
        FIT: [1-2 sentence assessment]
        RECOMMENDATION: [application strategy advice]
        """
    
    def suggest_search_terms(self):
        """Suggest search terms based on profile"""
        profile_skills = self.profile.get('skills', [])
        profile_experience = self.profile.get('experience', [])
        
        suggestions = []
        
        # Basic suggestions based on skills
        if 'Python' in str(profile_skills):
            suggestions.extend(['Python Developer', 'Python Engineer', 'Backend Developer'])
        if 'Machine Learning' in str(profile_skills) or 'AI' in str(profile_skills):
            suggestions.extend(['Machine Learning Engineer', 'Data Scientist', 'AI Engineer'])
        if 'JavaScript' in str(profile_skills):
            suggestions.extend(['Full Stack Developer', 'Frontend Developer'])
        
        # Add generic ones if needed
        if not suggestions:
            suggestions = ['Software Engineer', 'Developer', 'Engineer']
        
        # Return unique suggestions
        return list(set(suggestions))[:5]
    
    def chat_response(self, prompt, context):
        """Generate chat response using Claude"""
        try:
            # Build context string
            context_str = f"""
            Current job search status:
            - Total jobs in database: {context.get('total_jobs', 0)}
            - Jobs applied to: {context.get('applied', 0)}
            - High matches (80+): {len(context.get('top_matches', []))}
            
            Top matching jobs:
            """
            
            for job in context.get('top_matches', [])[:3]:
                context_str += f"\n- {job['title']} at {job['company']} (Score: {job['ai_score']})"
            
            response = self.client.messages.create(
                model='claude-3-5-sonnet-20241022',
                max_tokens=1000,
                messages=[{
                    'role': 'user',
                    'content': f"""{context_str}
                    
                    User question: {prompt}
                    
                    Provide helpful, specific advice about their job search."""
                }]
            )
            return response.content[0].text
        except Exception as e:
            return f"I can help you with your job search. What would you like to know? (Error: {str(e)})"
        
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse Claude's response properly"""
        
        analysis = {
            'score': 0,
            'strengths': [],
            'concerns': [],
            'fit_assessment': '',
            'recommendation': '',
            'raw_response': response_text,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Score extraction (works fine)
        score_match = re.search(r'SCORE:\s*(\d+)', response_text, re.IGNORECASE)
        if score_match:
            analysis['score'] = int(score_match.group(1))
        
        # Extract STRENGTHS section
        strengths_match = re.search(r'STRENGTHS:(.*?)(?=CONCERNS:|$)', response_text, re.DOTALL)
        if strengths_match:
            strengths_text = strengths_match.group(1)
            analysis['strengths'] = [s.strip('- ').strip() for s in strengths_text.strip().split('\n') if s.strip().startswith('-')]
        
        # Extract CONCERNS section
        concerns_match = re.search(r'CONCERNS:(.*?)(?=FIT:|$)', response_text, re.DOTALL)
        if concerns_match:
            concerns_text = concerns_match.group(1)
            analysis['concerns'] = [c.strip('- ').strip() for c in concerns_text.strip().split('\n') if c.strip().startswith('-')]
        
        # Extract FIT section (everything after "FIT:" until "RECOMMENDATION:" or end)
        fit_match = re.search(r'FIT:\s*(.*?)(?=RECOMMENDATION:|$)', response_text, re.DOTALL)
        if fit_match:
            analysis['fit_assessment'] = fit_match.group(1).strip()
        
        # Extract RECOMMENDATION section (everything after "RECOMMENDATION:" until end)
        rec_match = re.search(r'RECOMMENDATION:\s*(.*)', response_text, re.DOTALL)
        if rec_match:
            analysis['recommendation'] = rec_match.group(1).strip()
        
        return analysis
    
    def _get_fallback_analysis(self) -> Dict:
        """Return basic analysis if API call fails"""
        return {
            'score': 50,
            'strengths': ['Unable to analyze - API error'],
            'concerns': ['Analysis failed'],
            'fit_assessment': 'Could not complete analysis',
            'recommendation': 'Manual review required',
            'raw_response': '',
            'analyzed_at': datetime.now().isoformat()
        }
    
    def generate_cover_letter(self, job_data: Dict, analysis: Optional[Dict] = None) -> str:
        """Generate a personalized cover letter using Claude"""
        
        print(f'\\n✍️  Generating cover letter for {job_data.get("company")}...')
        
        # If no analysis provided, run one first
        if not analysis:
            analysis = self.analyze_job_fit(job_data)
        
        prompt = self._create_cover_letter_prompt(job_data, analysis)
        
        try:
            response = self.client.messages.create(
                model='claude-3-5-sonnet-20241022',
                max_tokens=1500,
                temperature=0.7,  # Higher temperature for more creative writing
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            cover_letter = response.content[0].text.strip()
            print(f'  ✓ Generated {len(cover_letter)} character cover letter')
            return cover_letter
            
        except Exception as e:
            print(f'  ❌ Error generating cover letter: {e}')
            return self._get_fallback_cover_letter(job_data)
    
    def _create_cover_letter_prompt(self, job_data: Dict, analysis: Dict) -> str:
        """Create prompt for cover letter generation"""
        
        return f"""Write a compelling cover letter for Yigit Bezek applying to:

JOB: {job_data.get('title')} at {job_data.get('company')}
LOCATION: {job_data.get('location')}

JOB DESCRIPTION:
{job_data.get('description', '')[:2000]}

CANDIDATE STRENGTHS (from analysis):
{chr(10).join('- ' + s for s in analysis.get('strengths', []))}

CANDIDATE PROFILE HIGHLIGHTS:
- BSc Creative Technology from University of Twente (2025)
- AI Facility Layout Optimizer thesis (20% throughput improvement)
- Software Developer at PSA International (multi-agent AI system)
- Projects: Computer Vision Climbing Assistant, Autonomous Drones, IoT systems
- Skills: Python, PyTorch, Machine Learning, Full-Stack Development
- Currently on orientation year visa in Netherlands (valid until 2026)

INSTRUCTIONS:
1. Keep it concise (250-350 words)
2. Start with enthusiasm for the specific role and company
3. Highlight 2-3 most relevant experiences/projects
4. Explain why Yigit is a great fit for THIS specific role
5. Address visa status naturally if relevant
6. Close with eagerness to discuss further
7. Professional but genuine tone
8. Use \"I\" statements, first person
9. Don't repeat job description verbatim

Write only the cover letter body (no \"Dear Hiring Manager\" or signature - that will be added separately).
"""
    
    def _get_fallback_cover_letter(self, job_data: Dict) -> str:
        """Basic cover letter template if API fails"""
        return f"""I am writing to express my strong interest in the {job_data.get('title')} position at {job_data.get('company')}.

As a recent BSc Creative Technology graduate from the University of Twente with hands-on experience in AI/ML and software development, I am excited about the opportunity to contribute to your team.

During my thesis, I developed an AI Facility Layout Optimizer using genetic algorithms that achieved a 20% throughput improvement. I have also worked as a Software Developer at PSA International, where I designed a multi-agent AI system for port workers. My technical skills include Python, PyTorch, machine learning, and full-stack development.

I am currently in the Netherlands on an orientation year visa (valid until 2026) and am eager to begin my professional career. I would welcome the opportunity to discuss how my background aligns with your needs.

Thank you for your consideration."""
    
    def batch_analyze_jobs(self, jobs: list) -> list:
        """Analyze multiple jobs and return sorted by score"""
        print(f'\\n🤖 Analyzing {len(jobs)} jobs with AI...')
        
        analyzed_jobs = []
        for i, job in enumerate(jobs, 1):
            print(f'\\n[{i}/{len(jobs)}]', end=' ')
            
            analysis = self.analyze_job_fit(job)
            
            # Merge analysis into job data
            job['ai_analysis'] = analysis
            job['ai_score'] = analysis['score']
            analyzed_jobs.append(job)
        
        # Sort by score
        analyzed_jobs.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        
        print(f'\\n✅ Completed analyzing {len(analyzed_jobs)} jobs')
        return analyzed_jobs


# Test function
if __name__ == '__main__':
    print('Testing AI Job Analyzer...\\n')
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print('❌ ANTHROPIC_API_KEY not set!')
        print('Set it with: export ANTHROPIC_API_KEY="your-key-here"')
        print('Get your key at: https://console.anthropic.com/')
        exit(1)
    
    # Initialize analyzer
    analyzer = AIJobAnalyzer()
    
    # Test with sample job
    test_job = {
        'title': 'Junior Python Developer',
        'company': 'Test Tech Company',
        'location': 'Amsterdam, Netherlands',
        'description': '''
        We are looking for a Junior Python Developer to join our team.
        
        Requirements:
        - Bachelor's degree in Computer Science or related field
        - Experience with Python and machine learning
        - Knowledge of PyTorch or TensorFlow
        - Strong problem-solving skills
        - Team player with good communication
        
        Responsibilities:
        - Develop and maintain Python applications
        - Work on machine learning models
        - Collaborate with senior developers
        - Write clean, maintainable code
        
        We offer visa sponsorship for international candidates.
        '''
    }
    
    # Test analysis
    analysis = analyzer.analyze_job_fit(test_job)
    print(f'\\n📊 Analysis Results:')
    print(f'   Score: {analysis["score"]}/100')
    print(f'   Strengths: {len(analysis["strengths"])} found')
    print(f'   Concerns: {len(analysis["concerns"])} found')
    
    # Test cover letter
    cover_letter = analyzer.generate_cover_letter(test_job, analysis)
    print(f'\\n📄 Cover Letter Preview:')
    print(cover_letter[:200] + '...')
    
    print('\\n✅ All tests passed!')
    
    