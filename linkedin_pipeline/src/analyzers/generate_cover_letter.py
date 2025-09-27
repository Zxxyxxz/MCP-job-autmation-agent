#!/usr/bin/env python3
"""Generate Cover Letter for a Specific Job"""

import os
import sys
from database import JobTracker
from analyzer_ai import AIJobAnalyzer


def main():
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print('❌ Error: ANTHROPIC_API_KEY not set')
        print('Run: export ANTHROPIC_API_KEY=\"your-key-here\"')
        sys.exit(1)
    
    # Initialize
    tracker = JobTracker()
    analyzer = AIJobAnalyzer()
    
    # Get job ID from command line or show options
    if len(sys.argv) < 2:
        print('\\n📋 High-scoring jobs in database:\\n')
        jobs = tracker.get_high_score_jobs(min_score=60, limit=10)
        
        if not jobs:
            print('No analyzed jobs found. Run test_full_pipeline.py first!')
            sys.exit(1)
        
        for i, job in enumerate(jobs, 1):
            score = job.get('ai_score', 'N/A')
            print(f'{i}. [{score}/100] {job["title"]} at {job["company"]}')
            print(f'   ID: {job["id"]} | {job["location"]}')
            print()
        
        print('Usage: python3 generate_cover_letter.py <job_id>')
        print('Example: python3 generate_cover_letter.py 5')
        sys.exit(0)
    
    # Get specific job
    job_id = int(sys.argv[1])
    job = tracker.get_job(job_id)
    
    if not job:
        print(f'❌ Job ID {job_id} not found')
        sys.exit(1)
    
    print(f'\\n📄 Generating cover letter for:\\n')
    print(f'   {job["title"]} at {job["company"]}')
    print(f'   Score: {job.get("ai_score", "N/A")}/100')
    print()
    
    # Generate cover letter
    cover_letter = analyzer.generate_cover_letter(job)
    
    # Save to file
    filename = f'data/cover_letter_{job["company"].replace(" ", "_")}_{job_id}.txt'
    with open(filename, 'w') as f:
        f.write(f'Cover Letter for: {job["title"]} at {job["company"]}\\n')
        f.write(f'Date: {__import__("datetime").datetime.now().strftime("%Y-%m-%d")}\\n')
        f.write('='*70 + '\\n\\n')
        f.write(cover_letter)
        f.write('\\n\\n')
        f.write('Best regards,\\n')
        f.write('Yigit Bezek\\n')
        f.write('bezekyigit0@gmail.com\\n')
        f.write('+31 629 400 891\\n')
    
    print(f'\\n✅ Cover letter saved to: {filename}')
    print(f'\\n📄 Preview:\\n')
    print('='*70)
    print(cover_letter[:300] + '...')
    print('='*70)
    
    # Update database
    tracker.update_job(job_id, cover_letter=cover_letter)
    tracker.update_status(job_id, 'cover_letter_generated', 'Ready to apply')
    
    print(f'\\n✅ Database updated!')
    
    tracker.close()


if __name__ == '__main__':
    main()
