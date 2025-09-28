# src/email_monitor.py
import json
from datetime import datetime, timedelta

class EmailMonitor:
    def __init__(self, db):
        self.db = db
    
    def check_application_responses(self):
        """Monitor Gmail for job responses using MCP"""
        # Search for job-related emails from last 7 days
        since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Use conversation_search to find job-related emails
        search_query = "application confirmation interview offer rejection"
        
        # This would use the actual Gmail MCP tool
        # For now, showing the structure
        results = self.search_recent_emails(search_query, since_date)
        
        for email in results:
            self.process_job_email(email)
    
    def process_job_email(self, email):
        """Process and categorize job email"""
        subject = email.get('subject', '').lower()
        from_email = email.get('from', '')
        
        # Determine email type
        if 'confirmation' in subject or 'received' in subject:
            email_type = 'application_confirmed'
        elif 'interview' in subject:
            email_type = 'interview_invite'
        elif 'offer' in subject:
            email_type = 'offer'
        elif 'reject' in subject or 'unfortunately' in subject:
            email_type = 'rejection'
        else:
            email_type = 'other'
        
        # Try to match to a job
        company = self.extract_company_from_email(from_email)
        job = self.db.find_job_by_company(company)
        
        if job:
            # Update job status
            self.db.add_email_tracking(job['id'], email)
            
            if email_type == 'interview_invite':
                # Parse interview details and add to calendar
                self.schedule_interview(job, email)