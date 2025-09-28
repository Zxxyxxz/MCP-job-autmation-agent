# src/enhanced_pipeline.py
import streamlit as st
import pandas as pd
from database.enhanced_database import JobDatabase
from analyzers.analyzer_ai import AIJobAnalyzer
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.validated_enricher import ValidatedEnricher  # ADD THIS
from scrapers.smart_description_enricher import SmartDescriptionEnricher  # ADD THIS


class JobSearchPlatform:
    def __init__(self):
        self.db = JobDatabase()
        self.analyzer = AIJobAnalyzer()
        self.scraper = LinkedInScraper()
        self.enricher = SmartDescriptionEnricher()
    def get_statistics(self):
        """Get comprehensive database statistics"""
        stats = {}
        
        stats['total'] = self.conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        stats['analyzed'] = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE ai_score IS NOT NULL").fetchone()[0]
        stats['high_matches'] = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE ai_score >= 80").fetchone()[0]
        stats['applied'] = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'applied'").fetchone()[0]
        stats['enriched'] = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE description IS NOT NULL AND LENGTH(description) > 100").fetchone()[0]
        stats['need_enrichment'] = stats['total'] - stats['enriched']
        stats['need_analysis'] = stats['enriched'] - stats['analyzed']
        
        return stats
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
    
    def analyze_with_validation(self, job):
        """Analyze job with full validation pipeline"""
        
        # Step 1: Validate existing description
        if not job.get('description') or len(job['description']) < 500:
            print(f"⚠️ Insufficient description for {job['title']}")
            
            # Step 2: Re-fetch with validation
            if not hasattr(self.enricher, 'driver'):
                self.enricher.setup_driver()
            
            enricher = ValidatedEnricher(self.enricher.driver)  # Use enricher's driver
            enrichment_result = enricher.fetch_with_validation(job['url'])
            
            if enrichment_result['quality_score'] < 50:
                print(f"❌ Poor quality enrichment, skipping analysis")
                return None
            
            job['description'] = enrichment_result['description']
            job['enrichment_metadata'] = enrichment_result
        
        # Step 3: Pre-qualification check
        qualification = self.analyzer.pre_qualify_job(job, job.get('enrichment_metadata', {}))
        
        if not qualification['qualified']:
            print(f"❌ Disqualified: {', '.join(qualification['disqualifiers'])}")
            job['analysis'] = {
                'score': 20,
                'disqualified': True,
                'reasons': qualification['disqualifiers']
            }
            return job
        
        # Step 4: Full analysis only if qualified - pass enrichment_result
        analysis = self.analyzer.analyze_job_fit(job, job.get('enrichment_metadata'))
        job['analysis'] = analysis
        
        return job
    
    def analyze_new_jobs(self):
        """Analyze all unanalyzed jobs"""
        jobs = self.db.get_jobs_for_analysis()
        
        for job in jobs:
            print(f"Analyzing {job['title']} at {job['company']}...")
            analysis = self.analyzer.analyze_job_fit(job)
            self.db.update_analysis(job['id'], analysis)
        
        return len(jobs)