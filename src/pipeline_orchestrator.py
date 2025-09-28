# src/pipeline_orchestrator.py
#!/usr/bin/env python3
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Fix imports
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.smart_description_enricher import SmartDescriptionEnricher
from analyzers.analyzer_ai import AIJobAnalyzer
from database.database import JobTracker

class JobSearchPipeline:
    def __init__(self):
        self.scraper = LinkedInScraper()
        self.enricher = SmartDescriptionEnricher()
        self.analyzer = AIJobAnalyzer()
        self.database = JobTracker()
        
    def run_full_pipeline(self, query="Python Developer", location="Netherlands"):
        """Complete end-to-end pipeline"""
        
        print("="*60)
        print("AUTOMATED JOB SEARCH PIPELINE")
        print("="*60)
        
        # Step 1: Scrape
        print("\n📡 Step 1: Scraping Jobs...")
        jobs = self.scraper.scrape_jobs(query, location)
        print(f"Found {len(jobs)} jobs")
        
        # Step 2: Check cache for descriptions
        print("\n🔍 Step 2: Enriching with Descriptions...")
        jobs_needing_enrichment = []
        
        for job in jobs:
            # Check if we already have this job in DB with description
            existing = self.database.get_job_by_url(job['url'])
            if existing and existing.get('description'):
                job['description'] = existing['description']
                print(f"  ✓ Using cached: {job['title'][:30]}")
            else:
                jobs_needing_enrichment.append(job)
        
        # Enrich only new jobs
        if jobs_needing_enrichment:
            print(f"  Fetching {len(jobs_needing_enrichment)} new descriptions...")
            for job in jobs_needing_enrichment:
                desc = self.enricher.fetch_with_retry(job['url'])
                job['description'] = desc
                print(f"  {'✓' if desc else '✗'} {job['title'][:30]}")
        
        # Step 3: Analyze with AI
        print("\n🤖 Step 3: AI Analysis...")
        analyzed_jobs = []
        
        for job in jobs:
            if not job.get('description'):
                continue
                
            # Check if already analyzed
            existing = self.database.get_job_by_url(job['url'])
            if existing and existing.get('ai_score'):
                job['ai_analysis'] = {
                    'score': existing['ai_score'],
                    'cached': True
                }
                print(f"  ✓ Cached score: {existing['ai_score']}/100 - {job['title'][:30]}")
            else:
                analysis = self.analyzer.analyze_job_fit(job)
                job['ai_analysis'] = analysis
                print(f"  ✓ New score: {analysis['score']}/100 - {job['title'][:30]}")
            
            analyzed_jobs.append(job)
            
            # Save to database
            self.database.upsert_job(job)
        
        # Step 4: Generate recommendations
        print("\n🎯 Step 4: Top Recommendations...")
        analyzed_jobs.sort(key=lambda x: x.get('ai_analysis', {}).get('score', 0), reverse=True)
        
        for i, job in enumerate(analyzed_jobs[:5], 1):
            score = job.get('ai_analysis', {}).get('score', 0)
            print(f"\n{i}. [{score}/100] {job['title']} at {job['company']}")
            print(f"   📍 {job['location']}")
            print(f"   🔗 {job['url'][:50]}...")
            
            if score >= 80:
                print("   ⚡ HIGH PRIORITY - Apply immediately!")
            elif score >= 70:
                print("   ✅ Good match - Apply soon")
            elif score >= 60:
                print("   📝 Decent match - Consider applying")
        
        # Step 5: Save report
        self.generate_report(analyzed_jobs)
        
        return analyzed_jobs
    
    def generate_report(self, jobs):
        """Generate actionable report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = {
            'generated_at': timestamp,
            'total_jobs': len(jobs),
            'high_priority': [j for j in jobs if j.get('ai_analysis', {}).get('score', 0) >= 80],
            'good_matches': [j for j in jobs if 70 <= j.get('ai_analysis', {}).get('score', 0) < 80],
            'all_jobs': jobs
        }
        
        with open(f'data/pipeline_report_{timestamp}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved: data/pipeline_report_{timestamp}.json")