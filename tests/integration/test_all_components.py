#!/usr/bin/env python3
"""Integration tests: verify all core components can be imported and initialized."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestModuleImports:
    def test_import_scraper(self):
        from scrapers.linkedin_scraper import LinkedInScraper
        assert LinkedInScraper is not None

    def test_import_database(self):
        from database.database import JobDatabase, JobTracker
        assert JobDatabase is JobTracker

    @pytest.mark.skipif(
        not os.getenv('ANTHROPIC_API_KEY'),
        reason='ANTHROPIC_API_KEY not set',
    )
    def test_import_analyzer(self):
        from analyzers.analyzer_ai import AIJobAnalyzer
        analyzer = AIJobAnalyzer()
        assert analyzer is not None


class TestLinkedInScraper:
    def test_init(self):
        from scrapers.linkedin_scraper import LinkedInScraper
        scraper = LinkedInScraper()
        assert scraper is not None

    def test_scrape_returns_list(self):
        from scrapers.linkedin_scraper import LinkedInScraper
        scraper = LinkedInScraper()
        jobs = scraper.scrape_jobs('python', 'Netherlands', 'week')
        assert isinstance(jobs, list)

    def test_job_structure(self):
        from scrapers.linkedin_scraper import LinkedInScraper
        scraper = LinkedInScraper()
        jobs = scraper.scrape_jobs('python', 'Netherlands', 'week')
        if jobs:
            required = {'title', 'company', 'url'}
            assert required.issubset(jobs[0].keys())


class TestDatabaseOperations:
    def test_init_and_add_job(self):
        from database.database import JobDatabase
        with tempfile.TemporaryDirectory() as tmpdir:
            db = JobDatabase(db_path=os.path.join(tmpdir, 'test.db'))
            job_id = db.add_job({
                'title': 'Test Job',
                'company': 'Test Company',
                'url': 'https://test.com/job/12345',
                'location': 'Test Location',
                'description': 'Test description',
            })
            assert job_id is not None
            stats = db.get_statistics()
            assert stats['total'] >= 1
            db.close()


class TestConfigFiles:
    def test_settings_json_loadable(self):
        settings_path = Path(__file__).parent.parent.parent / 'config' / 'settings.json'
        if settings_path.exists():
            with open(settings_path) as f:
                config = json.load(f)
            assert 'search_settings' in config
            assert 'browser' in config

    def test_profile_json_loadable(self):
        profile_path = Path(__file__).parent.parent.parent / 'config' / 'yigit_profile.json'
        if profile_path.exists():
            with open(profile_path) as f:
                profile = json.load(f)
            assert 'education' in profile or 'skills' in profile or 'technical_skills' in profile


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
