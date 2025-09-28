#!/usr/bin/env python3
"""Complete job search pipeline with descriptions"""

import sys
from pathlib import Path
sys.path.insert(0, 'src')

import json
from scrapers.description_enricher import DescriptionEnricher
from analyzers.analyzer_ai import AIJobAnalyzer

def main():
    print("="*60)
    print("COMPLETE JOB SEARCH PIPELINE")
    print("="*60)
    
    # Step 1: Check for scraped jobs
    jobs_file = 'data/linkedin_jobs_20250927_134329.json'
    if not Path(jobs_file).exists():
        print(f"Error: {jobs_file} not found")
        return
    
    # Step 2: Enrich with descriptions
    print("\n1. ENRICHING JOBS WITH DESCRIPTIONS")
    print("-"*40)
    enricher = DescriptionEnricher()
    enriched_jobs = enricher.enrich_jobs(jobs_file)
    
    # Step 3: Analyze with Claude
    print("\n2. ANALYZING WITH CLAUDE AI")
    print("-"*40)
    analyzer = AIJobAnalyzer()
    
    # Analyze top 5 jobs
    results = []
    for job in enriched_jobs[:5]:
        if not job.get('description'):
            continue
            
        print(f"\nAnalyzing: {job['title']}")
        analysis = analyzer.analyze_job_fit(job)
        job['ai_analysis'] = analysis
        results.append(job)
    
    # Step 4: Show results
    print("\n3. TOP MATCHES")
    print("-"*40)
    
    results.sort(key=lambda x: x['ai_analysis']['score'], reverse=True)
    
    for i, job in enumerate(results[:3], 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Score: {job['ai_analysis']['score']}/100")
        print(f"   Fit: {job['ai_analysis']['fit_assessment']}")
    
    # Save results
    with open('data/analyzed_jobs.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Results saved to data/analyzed_jobs.json")

if __name__ == '__main__':
    main()
