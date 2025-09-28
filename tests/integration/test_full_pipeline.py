#!/usr/bin/env python3
"""Complete Pipeline Test: Scraper → Database → AI Analysis"""

import os
import sys
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.database import JobTracker

# Check if API key is set
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print('=' * 70)
    print('⚠️  ANTHROPIC_API_KEY not set!')
    print('=' * 70)
    print()
    print('To use AI analysis, you need an Anthropic API key.')
    print()
    print('Quick setup:')
    print('1. Get key from: https://console.anthropic.com/')
    print('2. Run: export ANTHROPIC_API_KEY=\"your-key-here\"')
    print('3. Run this script again')
    print()
    print('For now, running WITHOUT AI analysis (scraper + database only)...')
    print('=' * 70)
    ai_enabled = False
else:
    from analyzer_ai import AIJobAnalyzer
    ai_enabled = True
    print('✅ AI Analysis enabled!')


def main():
    print()
    print('=' * 70)
    print('🚀 COMPLETE JOB PIPELINE TEST')
    print('=' * 70)
    
    # Step 1: Initialize components
    print('\\n📦 Step 1: Initializing components...')
    tracker = JobTracker()
    scraper = LinkedInScraper()
    if ai_enabled:
        analyzer = AIJobAnalyzer()
    print('✅ All components initialized')
    
    # Step 2: Scrape jobs
    print('\\n🔍 Step 2: Scraping jobs from LinkedIn...')
    jobs = scraper.scrape_jobs(
        query='python developer OR machine learning engineer',
        location='Netherlands',
        time_filter='week'
    )
    print(f'✅ Found {len(jobs)} jobs')
    
    if not jobs:
        print('❌ No jobs found. Try a different query or check internet connection.')
        return
    
    # Step 3: Add to database
    print('\\n💾 Step 3: Adding jobs to database...')
    added = 0
    skipped = 0
    
    for job in jobs:
        try:
            job_id = tracker.add_job(job)
            job['db_id'] = job_id
            added += 1
        except Exception as e:
            skipped += 1
    
    print(f'✅ Added {added} new jobs')
    if skipped > 0:
        print(f'⊘ Skipped {skipped} duplicates')
    
    # Step 4: AI Analysis (if enabled)
    if ai_enabled and jobs:
        print('\\n🤖 Step 4: Analyzing jobs with Claude AI...')
        print('(This may take a minute...)')
        
        # Analyze each job
        analyzed_jobs = []
        for i, job in enumerate(jobs[:5], 1):  # Analyze first 5 jobs as demo
            print(f'\\n  [{i}/5] Analyzing: {job["title"][:50]}...')
            
            try:
                # Get AI analysis
                analysis = analyzer.analyze_job_fit(job)
                
                # Update database with AI analysis
                tracker.update_job(
                    job['db_id'],
                    ai_score=analysis['score'],
                    ai_match_reasoning=analysis['fit_assessment'],
                    ai_strengths=json.dumps(analysis['strengths']),
                    ai_concerns=json.dumps(analysis['concerns']),
                    ai_recommendation=analysis['recommendation']
                )
                
                # Mark as analyzed
                tracker.update_status(job['db_id'], 'ai_analyzed', f'Score: {analysis["score"]}/100')
                
                job['ai_analysis'] = analysis
                analyzed_jobs.append(job)
                
                print(f'    ✓ Score: {analysis["score"]}/100')
                
            except Exception as e:
                print(f'    ❌ Analysis failed: {e}')
        
        print(f'\\n✅ Analyzed {len(analyzed_jobs)} jobs')
        
        # Show top matches
        if analyzed_jobs:
            analyzed_jobs.sort(key=lambda x: x.get('ai_analysis', {}).get('score', 0), reverse=True)
            
            print('\\n' + '=' * 70)
            print('🎯 TOP MATCHES')
            print('=' * 70)
            
            for i, job in enumerate(analyzed_jobs[:3], 1):
                analysis = job['ai_analysis']
                print(f'\\n{i}. {job["title"]} at {job["company"]}')
                print(f'   Score: {analysis["score"]}/100 | Location: {job["location"]}')
                print(f'   URL: {job["url"][:70]}...')
                print(f'\\n   Why it\'s a good fit:')
                print(f'   {analysis["fit_assessment"][:150]}...')
                print(f'\\n   Top Strengths:')
                for strength in analysis['strengths'][:2]:
                    print(f'   • {strength}')
    else:
        print('\\n⊘ Step 4: AI Analysis skipped (no API key)')
    
    # Step 5: Database statistics
    print('\\n' + '=' * 70)
    print('📊 DATABASE STATISTICS')
    print('=' * 70)
    
    stats = tracker.get_statistics()
    print(f'\\nTotal jobs in database: {stats["total_jobs"]}')
    print(f'Average AI score: {stats["average_ai_score"]}/100')
    print(f'\\nJobs by status:')
    for status, count in stats['by_status'].items():
        print(f'  • {status}: {count}')
    
    # Step 6: Show next steps
    print('\\n' + '=' * 70)
    print('✅ PIPELINE TEST COMPLETE!')
    print('=' * 70)
    
    print('\\n📋 What you can do now:')
    print('\\n1. View all jobs:')
    print('   python3 -c "from database import JobTracker; t=JobTracker(); [print(j[\'title\'], \'at\', j[\'company\']) for j in t.get_recent_jobs()]"')
    
    if ai_enabled:
        print('\\n2. View high-scoring jobs:')
        print('   python3 -c "from database import JobTracker; t=JobTracker(); [print(f\'{j[\"title\"]}: {j[\"ai_score\"]}/100\') for j in t.get_high_score_jobs(70)]"')
        
        print('\\n3. Generate cover letter for top job:')
        print('   # Edit and run: test_cover_letter.py')
    
    print('\\n4. Check database directly:')
    print('   sqlite3 data/jobs.db "SELECT title, company, ai_score, status FROM jobs ORDER BY ai_score DESC LIMIT 10;"')
    
    print('\\n5. Export all data:')
    print('   python3 -c "from database import JobTracker; JobTracker().export_to_json(\'data/all_jobs.json\')"')
    
    print('\\n📁 Database: data/jobs.db')
    print('📊 Statistics: Run this script again anytime to update!')
    
    tracker.close()


if __name__ == '__main__':
    import json
    main()
