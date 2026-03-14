#!/usr/bin/env python3
"""Integration test: Scraper -> Database storage and status tracking."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scrapers.linkedin_scraper import LinkedInScraper
from database.database import JobDatabase


@pytest.fixture
def tracker():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = JobDatabase(db_path=os.path.join(tmpdir, 'test.db'))
        yield db
        db.close()


@pytest.fixture
def scraper():
    return LinkedInScraper()


class TestScraperDatabaseIntegration:
    def test_scrape_and_store(self, scraper, tracker):
        jobs = scraper.scrape_jobs('junior software engineer', 'Netherlands', 'week')
        assert isinstance(jobs, list)

        added = 0
        for job in jobs[:5]:
            job_id = tracker.add_job(job)
            if job_id is not None:
                added += 1

        stats = tracker.get_statistics()
        assert stats['total'] >= added

    def test_status_update_and_history(self, tracker):
        job_id = tracker.add_job({
            'title': 'Integration Test Job',
            'company': 'TestCo',
            'location': 'Amsterdam',
            'url': 'https://www.linkedin.com/jobs/view/integration-test',
            'description': 'Test description for integration test.',
        })
        assert job_id is not None

        tracker.update_status(job_id, 'reviewed', 'Looks promising')
        history = tracker.get_job_history(job_id)
        assert len(history) >= 2  # scraped + status_change

    def test_recent_jobs(self, tracker):
        tracker.add_job({
            'title': 'Recent Job',
            'company': 'RecentCo',
            'location': 'Rotterdam',
            'url': 'https://www.linkedin.com/jobs/view/recent-test',
            'description': 'Recent test.',
        })
        recent = tracker.get_recent_jobs(limit=5)
        assert len(recent) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
