"""
Job Tracking Database
SQLite-based system for tracking job applications through entire lifecycle
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class JobTracker:
    """Track jobs from scraping to offer/rejection"""
    
    def __init__(self, db_path='data/jobs.db'):
        """Initialize database connection"""
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else 'data', exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                source TEXT DEFAULT 'linkedin',
                scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_date TIMESTAMP,
                response_date TIMESTAMP,
                interview_date TIMESTAMP,
                offer_date TIMESTAMP,
                rejection_date TIMESTAMP,
                status TEXT DEFAULT 'scraped',
                ai_score INTEGER,
                ai_match_reasoning TEXT,
                ai_strengths TEXT,
                ai_concerns TEXT,
                ai_recommendation TEXT,
                cover_letter TEXT,
                resume_version TEXT,
                recruiter_name TEXT,
                recruiter_email TEXT,
                last_followup_date TIMESTAMP,
                followup_count INTEGER DEFAULT 0,
                notes TEXT,
                salary_range TEXT,
                remote_option TEXT,
                visa_sponsorship BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                subject TEXT,
                sender TEXT,
                recipient TEXT,
                body TEXT,
                received_date TIMESTAMP,
                email_type TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                interview_type TEXT,
                scheduled_date TIMESTAMP,
                duration_minutes INTEGER,
                interviewer_name TEXT,
                interviewer_title TEXT,
                location TEXT,
                notes TEXT,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        ''')
        
        self.conn.commit()
        print('✅ Database tables created successfully!')
    
    def add_job(self, job_data: Dict) -> int:
        """Add a new job to the database"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO jobs (
                    job_id, title, company, location, url, description, source, scraped_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('job_id'),
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('location'),
                job_data.get('url'),
                job_data.get('description', ''),
                job_data.get('source', 'linkedin'),
                job_data.get('scraped_at', datetime.now().isoformat())
            ))
            
            job_id = cursor.lastrowid
            self.log_action(job_id, 'scraped', f'Job scraped from {job_data.get("source", "linkedin")}')
            self.conn.commit()
            return job_id
            
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM jobs WHERE url = ?', (job_data.get('url'),))
            existing_job = cursor.fetchone()
            if existing_job:
                return existing_job[0]
            raise
    
    def update_job(self, job_id: int, **kwargs):
        """Update job fields"""
        cursor = self.conn.cursor()
        fields = []
        values = []
        for key, value in kwargs.items():
            if key != 'id':
                fields.append(f'{key} = ?')
                values.append(value)
        fields.append('updated_at = ?')
        values.append(datetime.now().isoformat())
        values.append(job_id)
        query = f'UPDATE jobs SET {", ".join(fields)} WHERE id = ?'
        cursor.execute(query, values)
        self.conn.commit()
    
    def update_status(self, job_id: int, new_status: str, notes: str = None):
        """Update job status with logging"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT status FROM jobs WHERE id = ?', (job_id,))
        old_status = cursor.fetchone()
        old_status = old_status[0] if old_status else 'unknown'
        cursor.execute('UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?', 
                      (new_status, datetime.now().isoformat(), job_id))
        action_detail = f'Status changed: {old_status} → {new_status}'
        if notes:
            action_detail += f' | {notes}'
        self.log_action(job_id, f'status_change_{new_status}', action_detail)
        self.conn.commit()
    
    def log_action(self, job_id: int, action: str, details: str = None):
        """Log an action in the history"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO application_history (job_id, action, details) VALUES (?, ?, ?)',
                      (job_id, action, details))
        self.conn.commit()
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get a single job by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_jobs_by_status(self, status: str) -> List[Dict]:
        """Get all jobs with a specific status"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE status = ? ORDER BY scraped_date DESC', (status,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_jobs(self, limit: int = 20) -> List[Dict]:
        """Get most recently scraped jobs"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs ORDER BY scraped_date DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_high_score_jobs(self, min_score: int = 70, limit: int = 20) -> List[Dict]:
        """Get jobs with high AI match scores"""
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM jobs WHERE ai_score >= ? 
                       ORDER BY ai_score DESC, scraped_date DESC LIMIT ?''',
                      (min_score, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_jobs_needing_followup(self, days_since_applied: int = 7) -> List[Dict]:
        """Get jobs that need follow-up"""
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM jobs WHERE status = 'applied' 
                       AND applied_date IS NOT NULL
                       AND (last_followup_date IS NULL OR 
                            julianday('now') - julianday(last_followup_date) > ?)
                       AND julianday('now') - julianday(applied_date) >= ?''',
                      (days_since_applied, days_since_applied))
        return [dict(row) for row in cursor.fetchall()]
    
    def search_jobs(self, query: str) -> List[Dict]:
        """Search jobs by title, company, or description"""
        cursor = self.conn.cursor()
        search_pattern = f'%{query}%'
        cursor.execute('''SELECT * FROM jobs WHERE title LIKE ? OR company LIKE ? 
                       OR description LIKE ? ORDER BY scraped_date DESC''',
                      (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get application statistics"""
        cursor = self.conn.cursor()
        stats = {}
        cursor.execute('SELECT COUNT(*) FROM jobs')
        stats['total_jobs'] = cursor.fetchone()[0]
        cursor.execute('SELECT status, COUNT(*) FROM jobs GROUP BY status')
        stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE status IN ("applied", "interview_scheduled", "interviewed", "offer")')
        stats['total_applications'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM interviews')
        stats['total_interviews'] = cursor.fetchone()[0]
        cursor.execute('SELECT AVG(ai_score) FROM jobs WHERE ai_score IS NOT NULL')
        avg_score = cursor.fetchone()[0]
        stats['average_ai_score'] = round(avg_score, 1) if avg_score else 0
        if stats['total_applications'] > 0:
            cursor.execute('SELECT COUNT(*) FROM jobs WHERE status IN ("interview_scheduled", "interviewed", "offer")')
            responses = cursor.fetchone()[0]
            stats['response_rate'] = round((responses / stats['total_applications']) * 100, 1)
        else:
            stats['response_rate'] = 0
        return stats
    
    def export_to_json(self, filename: str):
        """Export all jobs to JSON"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs')
        jobs = [dict(row) for row in cursor.fetchall()]
        with open(filename, 'w') as f:
            json.dump(jobs, f, indent=2, default=str)
        print(f'✅ Exported {len(jobs)} jobs to {filename}')
    

    def get_job_history(self, job_id: int) -> List[Dict]:
        """Get full history of a job"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM application_history WHERE job_id = ? ORDER BY timestamp ASC', (job_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_email(self, job_id: int, email_data: Dict):
        """Add an email to the database"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO emails (job_id, subject, sender, recipient, body, received_date, email_type) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (job_id, email_data.get('subject'), email_data.get('sender'), email_data.get('recipient'),
                       email_data.get('body'), email_data.get('received_date'), email_data.get('email_type')))
        self.conn.commit()
    
    def add_interview(self, job_id: int, interview_data: Dict) -> int:
        """Schedule an interview"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO interviews (job_id, interview_type, scheduled_date, duration_minutes, interviewer_name, interviewer_title, location, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                      (job_id, interview_data.get('interview_type'), interview_data.get('scheduled_date'),
                       interview_data.get('duration_minutes', 60), interview_data.get('interviewer_name'),
                       interview_data.get('interviewer_title'), interview_data.get('location'), interview_data.get('notes')))
        interview_id = cursor.lastrowid
        self.update_status(job_id, 'interview_scheduled', f'Interview scheduled for {interview_data.get("scheduled_date")}')
        self.conn.commit()
        return interview_id

    def close(self):
        """Close database connection"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == '__main__':
    print('Testing JobTracker Database...')
    tracker = JobTracker()
    test_job = {
        'job_id': 'test_123',
        'title': 'Senior Python Engineer',
        'company': 'Test Company',
        'location': 'Amsterdam',
        'url': 'https://linkedin.com/jobs/test',
        'description': 'Looking for a Python expert',
        'source': 'linkedin'
    }
    job_id = tracker.add_job(test_job)
    print(f'✅ Added test job with ID: {job_id}')
    tracker.update_status(job_id, 'reviewed', 'Looks interesting')
    print('✅ Updated job status')
    stats = tracker.get_statistics()
    print(f'✅ Database statistics: {stats}')
    print('\n✅ All database tests passed!')
