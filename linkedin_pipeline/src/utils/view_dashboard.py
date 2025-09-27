#!/usr/bin/env python3
"""Simple Dashboard View of Job Database"""

from database import JobTracker
import json


def main():
    tracker = JobTracker()
    
    print('\\n' + '='*70)
    print(' ' * 25 + '📊 JOB DASHBOARD')
    print('='*70)
    
    # Statistics
    stats = tracker.get_statistics()
    print(f'\\n📈 Overview:')
    print(f'   Total jobs: {stats["total_jobs"]}')
    print(f'   Applications sent: {stats["total_applications"]}')
    print(f'   Interviews: {stats["total_interviews"]}')
    print(f'   Average AI score: {stats["average_ai_score"]}/100')
    print(f'   Response rate: {stats["response_rate"]}%')
    
    # Jobs by status
    print(f'\\n📋 Jobs by Status:')
    for status, count in sorted(stats['by_status'].items(), key=lambda x: x[1], reverse=True):
        print(f'   {status:25} {count:3} jobs')
    
    # High-scoring jobs
    print(f'\\n🎯 Top 10 Jobs (by AI score):')
    high_score = tracker.get_high_score_jobs(min_score=0, limit=10)
    
    if high_score:
        for i, job in enumerate(high_score, 1):
            score = job.get('ai_score') or 0
            status = job.get('status', 'unknown')
            print(f'\\n   {i}. [{score}/100] {job["title"][:45]}')
            print(f'      Company: {job["company"]:30} Status: {status}')
            print(f'      Location: {job["location"]:28} ID: {job["id"]}')
    else:
        print('   No analyzed jobs yet. Run: python3 test_full_pipeline.py')
    
    # Jobs needing follow-up
    print(f'\\n🔔 Jobs Needing Follow-up:')
    followup = tracker.get_jobs_needing_followup(days_since_applied=7)
    if followup:
        for job in followup[:5]:
            print(f'   • {job["title"]} at {job["company"]}')
            print(f'     Applied: {job["applied_date"][:10]} (ID: {job["id"]})')
    else:
        print('   None (or no applications sent yet)')
    
    # Recent activity
    print(f'\\n🕐 Recent Jobs (Last 5):')
    recent = tracker.get_recent_jobs(limit=5)
    for job in recent:
        print(f'   • {job["title"]} at {job["company"]}')
        print(f'     Scraped: {job["scraped_date"][:10]} | Status: {job["status"]}')
    
    print('\\n' + '='*70)
    print('\\n💡 Quick Commands:')
    print('   View all jobs:        python3 view_dashboard.py')
    print('   Run full pipeline:    python3 test_full_pipeline.py')  
    print('   Generate cover letter: python3 generate_cover_letter.py <job_id>')
    print('   Export to JSON:       python3 -c "from database import JobTracker; JobTracker().export_to_json(\'jobs_export.json\')"')
    print('\\n📁 Database: data/jobs.db')
    print('='*70 + '\\n')
    
    tracker.close()


if __name__ == '__main__':
    main()
