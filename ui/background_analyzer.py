import streamlit as st
from datetime import datetime
import threading
import time

class BackgroundAnalyzer:
    # Class-level storage that persists across reruns
    _analysis_state = {
        'running': False,
        'current': 0,
        'total': 0,
        'start_time': None,
        'errors': []
    }
    _lock = threading.Lock()
    
    @classmethod
    def get_status(cls):
        """Thread-safe status getter"""
        with cls._lock:
            return cls._analysis_state.copy()
    
    @classmethod
    def analyze_jobs_async(cls, db, analyzer):
        """Run analysis without blocking the UI"""
        
        # Check if already running
        with cls._lock:
            if cls._analysis_state['running']:
                return False, "Analysis already running"
        
        # Get jobs needing analysis
        jobs = db.get_jobs_for_analysis()
        
        if not jobs:
            return False, "No jobs need analysis"
        
        # Initialize state
        with cls._lock:
            cls._analysis_state = {
                'running': True,
                'current': 0,
                'total': len(jobs),
                'start_time': datetime.now(),
                'errors': []
            }
        
        def run_analysis():
            """This runs in background thread"""
            for i, job in enumerate(jobs):
                # Check if cancelled
                with cls._lock:
                    if not cls._analysis_state['running']:
                        break
                    cls._analysis_state['current'] = i + 1
                
                try:
                    # Analyze job
                    analysis = analyzer.analyze_job_fit(job)
                    db.update_analysis(job['id'], analysis)
                    
                except Exception as e:
                    with cls._lock:
                        cls._analysis_state['errors'].append({
                            'job': job.get('title', 'Unknown'),
                            'error': str(e)
                        })
            
            # Mark complete
            with cls._lock:
                cls._analysis_state['running'] = False
        
        # Start background thread
        thread = threading.Thread(target=run_analysis, daemon=True)
        thread.start()
        
        return True, f"Started analyzing {len(jobs)} jobs"
    
    @classmethod
    def cancel_analysis(cls):
        """Cancel running analysis"""
        with cls._lock:
            cls._analysis_state['running'] = False