# src/enhanced_pipeline.py
import streamlit as st
import pandas as pd
from database.enhanced_database import JobDatabase
from analyzers.analyzer_ai import AIJobAnalyzer
from scrapers.linkedin_scraper import LinkedInScraper

class JobSearchPlatform:
    def __init__(self):
        self.db = JobDatabase()
        self.analyzer = AIJobAnalyzer()
        self.scraper = LinkedInScraper()
    
    def run_smart_search(self, search_terms=None, location="Netherlands"):
        """Smart search with AI-suggested terms"""
        if not search_terms:
            # Let Claude suggest search terms based on profile
            search_terms = self.analyzer.suggest_search_terms()
        
        all_jobs = []
        for term in search_terms:
            jobs = self.scraper.scrape_jobs(term, location)
            all_jobs.extend(jobs)
        
        # Store in database
        for job in all_jobs:
            job_id = self.db.add_job(job)
            job['id'] = job_id
        
        return all_jobs
    
    def analyze_new_jobs(self):
        """Analyze all unanalyzed jobs"""
        jobs = self.db.get_jobs_for_analysis()
        
        for job in jobs:
            print(f"Analyzing {job['title']} at {job['company']}...")
            analysis = self.analyzer.analyze_job_fit(job)
            self.db.update_analysis(job['id'], analysis)
        
        return len(jobs)