# src/application_manager.py
class ApplicationManager:
    def __init__(self, db, analyzer):
        self.db = db
        self.analyzer = analyzer
    
    def prepare_application(self, job_id):
        """Prepare full application materials"""
        job = self.db.get_job(job_id)
        
        # Get company information
        company_info = self.research_company(job['company'])
        job['company_info'] = company_info
        
        # Generate cover letter with full context
        cover_letter = self.analyzer.generate_cover_letter(
            job_data=job,
            company_research=company_info
        )
        
        # Store in database
        self.db.update_job(job_id, {
            'cover_letter': cover_letter,
            'status': 'ready_to_apply'
        })
        
        return {
            'job': job,
            'cover_letter': cover_letter,
            'apply_url': job['url']
        }
    
    def track_application(self, job_id):
        """Mark job as applied and start tracking"""
        self.db.update_job(job_id, {
            'status': 'applied',
            'applied_at': datetime.now().isoformat()
        })
        
        # Set reminder to follow up in 7 days
        self.schedule_followup(job_id, days=7)