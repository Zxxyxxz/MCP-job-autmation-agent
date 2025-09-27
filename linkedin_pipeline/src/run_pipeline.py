#!/usr/bin/env python3
"""
LinkedIn Job Pipeline Runner
Orchestrates the scraping and analysis process
"""

import os
import sys
import time
import json
from datetime import datetime

# Add subdirectories to path
sys.path.append('scrapers')
sys.path.append('analyzers')

from scrapers.linkedin_scraper import LinkedInScraper
from analyzers.job_analyzer import JobAnalyzer

class JobPipeline:
    def __init__(self):
        self.scraper = LinkedInScraper()
        self.analyzer = None
        
        # Ensure data and logs directories exist
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
    def run_full_pipeline(self, query=None, location=None, time_filter=None):
        """Run the complete job search and analysis pipeline"""
        print("="*60)
        print(f"🚀 LinkedIn Job Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # Step 1: Scrape jobs
        print("\n📥 Step 1: Scraping LinkedIn jobs...")
        jobs = self.scraper.scrape_jobs(query, location, time_filter)
        
        if not jobs:
            print("❌ No jobs found. Exiting.")
            return
        
        # Get the latest jobs file
        import glob
        files = glob.glob('data/linkedin_jobs_*.json')
        if not files:
            print("❌ No jobs file created. Exiting.")
            return
        
        latest_file = max(files, key=os.path.getctime)
        
        # Step 2: Analyze jobs
        print("\n🔍 Step 2: Analyzing job descriptions...")
        self.analyzer = JobAnalyzer()
        analyzed_jobs = self.analyzer.analyze_jobs_file(latest_file)
        
        # Step 3: Summary
        self.print_summary(analyzed_jobs)
        
        print("\n✅ Pipeline completed successfully!")
        print("\n📋 Check the ACTION_PLAN in the data/ directory for prioritized jobs.")
        
        return analyzed_jobs
    
    def print_summary(self, analyzed_jobs):
        """Print a summary of the analysis"""
        if not analyzed_jobs:
            return
        
        print("\n" + "="*60)
        print("📊 ANALYSIS SUMMARY")
        print("="*60)
        
        high_score = [j for j in analyzed_jobs if j.get('score', 0) >= 75]
        medium_score = [j for j in analyzed_jobs if 60 <= j.get('score', 0) < 75]
        
        print(f"\n🎯 High Priority Jobs (Score >= 75): {len(high_score)}")
        for job in high_score[:5]:
            print(f"  • {job['title'][:40]:40} | {job['company'][:20]:20} | Score: {job['score']}")
        
        print(f"\n📋 Medium Priority Jobs (Score 60-74): {len(medium_score)}")
        for job in medium_score[:3]:
            print(f"  • {job['title'][:40]:40} | {job['company'][:20]:20} | Score: {job['score']}")
        
    def search_multiple_queries(self, queries):
        """Run pipeline for multiple search queries"""
        all_jobs = []
        
        for query in queries:
            print(f"\n🔍 Searching for: {query}")
            jobs = self.run_full_pipeline(query=query)
            if jobs:
                all_jobs.extend(jobs)
            time.sleep(5)  # Wait between queries
        
        # Remove duplicates based on job URL
        unique_jobs = {job['url']: job for job in all_jobs}.values()
        
        print(f"\n📊 Total unique jobs found: {len(unique_jobs)}")
        return list(unique_jobs)

def main():
    """Main entry point"""
    pipeline = JobPipeline()
    
    # You can customize these searches
    queries = [
        "python developer",
        "software engineer graduate",
        "backend developer junior",
        "full stack developer entry level"
    ]
    
    # Run for a single query
    # pipeline.run_full_pipeline(query="python developer", location="Netherlands", time_filter="week")
    
    # Or run for multiple queries
    pipeline.search_multiple_queries(queries)

if __name__ == '__main__':
    main()
