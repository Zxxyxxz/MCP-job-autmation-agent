import sqlite3
from datetime import datetime
import json
import threading

class JobDatabase:
    _local = threading.local()
    
    def __init__(self, db_path='data/jobs.db'):
        self.db_path = db_path
        self.create_tables()
    
    @property
    def conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def create_tables(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                url TEXT UNIQUE,
                description TEXT,
                company_info TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                ai_score INTEGER,
                ai_strengths TEXT,
                ai_concerns TEXT, 
                ai_fit_assessment TEXT,
                ai_recommendation TEXT,
                analyzed_at TIMESTAMP,
                status TEXT DEFAULT 'new',
                applied_at TIMESTAMP,
                application_method TEXT,
                cover_letter TEXT,
                response_received BOOLEAN DEFAULT 0,
                response_date TIMESTAMP,
                response_type TEXT,
                interview_scheduled BOOLEAN DEFAULT 0,
                interview_date TIMESTAMP,
                interview_notes TEXT,
                outcome TEXT,
                outcome_date TIMESTAMP,
                notes TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS email_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                email_subject TEXT,
                email_from TEXT,
                email_date TIMESTAMP,
                email_type TEXT,
                processed BOOLEAN DEFAULT 0,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_job(self, job_data):
        """Add or update job in database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (title, company, location, url, description, source, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data['title'],
                job_data['company'],
                job_data.get('location', ''),
                job_data['url'],
                job_data.get('description', ''),
                job_data.get('source', 'linkedin'),
                datetime.now().isoformat()
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM jobs WHERE url = ?", (job_data['url'],))
            row = cursor.fetchone()
            return row[0] if row else None
    def job_exists(self, url):
        """Check if job already exists in database"""
        cursor = self.conn.execute("SELECT id FROM jobs WHERE url = ?", (url,))
        return cursor.fetchone() is not None

    def get_jobs_needing_description(self, limit=10):
        """Get jobs that need description enrichment"""
        cursor = self.conn.execute('''
            SELECT * FROM jobs 
            WHERE (description IS NULL OR LENGTH(description) < 100)
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def update_job_description(self, job_id, description):
        """Update only the description for a job"""
        self.conn.execute(
            "UPDATE jobs SET description = ? WHERE id = ?",
            (description, job_id)
        )
        self.conn.commit()
    
    def update_apply_link(self, job_id, apply_link):
        """Update job with direct apply link"""
        self.conn.execute(
            "UPDATE jobs SET application_link = ? WHERE id = ?",
            (apply_link, job_id)
        )
        self.conn.commit()
    
    def get_statistics(self):
        """Get comprehensive database statistics"""
        stats = {}
        
        # Total jobs
        stats['total'] = self.conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        
        # Jobs by enrichment status
        stats['enriched'] = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE description IS NOT NULL AND LENGTH(description) > 100"
        ).fetchone()[0]
        stats['need_enrichment'] = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE description IS NULL OR LENGTH(description) < 100"
        ).fetchone()[0]
        
        # Jobs by analysis status
        stats['analyzed'] = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE ai_score IS NOT NULL"
        ).fetchone()[0]
        stats['need_analysis'] = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE ai_score IS NULL AND LENGTH(COALESCE(description, '')) > 100"
        ).fetchone()[0]
        
        # Jobs by status
        stats['new'] = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'new'").fetchone()[0]
        stats['applied'] = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'applied'").fetchone()[0]
        stats['skipped'] = self.conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'skipped'").fetchone()[0]
        
        # Score distribution
        stats['high_matches'] = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE ai_score >= 80"
        ).fetchone()[0]
        stats['medium_matches'] = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE ai_score >= 60 AND ai_score < 80"
        ).fetchone()[0]
        stats['low_matches'] = self.conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE ai_score < 60 AND ai_score IS NOT NULL"
        ).fetchone()[0]
        
        return stats

    def mark_job_enriched(self, job_id):
        """Mark a job as enriched with timestamp"""
        self.conn.execute(
            "UPDATE jobs SET enriched_at = ? WHERE id = ?",
            (datetime.now().isoformat(), job_id)
        )
        self.conn.commit()

    def mark_job_analyzed(self, job_id):
        """Mark a job as analyzed with timestamp"""
        self.conn.execute(
            "UPDATE jobs SET analyzed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), job_id)
        )
        self.conn.commit()
        
    def update_analysis(self, job_id, analysis):
        """Update job with AI analysis"""
        self.conn.execute('''
            UPDATE jobs SET
                ai_score = ?,
                ai_strengths = ?,
                ai_concerns = ?,
                ai_fit_assessment = ?,
                ai_recommendation = ?,
                analyzed_at = ?
            WHERE id = ?
        ''', (
            analysis.get('score', 0),
            json.dumps(analysis.get('strengths', [])),
            json.dumps(analysis.get('concerns', [])),
            analysis.get('fit_assessment', ''),
            analysis.get('recommendation', ''),
            datetime.now().isoformat(),
            job_id
        ))
        self.conn.commit()
    
    def get_jobs_for_analysis(self):
        """Get jobs that need analysis"""
        cursor = self.conn.execute('''
            SELECT * FROM jobs 
            WHERE ai_score IS NULL 
            AND description IS NOT NULL 
            AND LENGTH(description) > 100
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_jobs_by_score(self, min_score=70):
        """Get analyzed jobs sorted by score"""
        cursor = self.conn.execute('''
            SELECT * FROM jobs 
            WHERE ai_score >= ? 
            ORDER BY ai_score DESC
        ''', (min_score,))
        return [dict(row) for row in cursor.fetchall()]