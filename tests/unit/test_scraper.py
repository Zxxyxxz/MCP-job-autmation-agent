"""Unit tests for LinkedInScraper."""

import pytest
from scrapers.linkedin_scraper import LinkedInScraper


class TestLinkedInScraper:
    def test_init(self):
        scraper = LinkedInScraper()
        assert scraper.headers is not None
        assert 'User-Agent' in scraper.headers

    def test_scrape_returns_list(self):
        scraper = LinkedInScraper()
        jobs = scraper.scrape_jobs('python developer', 'Netherlands')
        assert isinstance(jobs, list)

    def test_scrape_with_time_filter(self):
        scraper = LinkedInScraper()
        jobs = scraper.scrape_jobs('python developer', 'Netherlands', time_filter='week')
        assert isinstance(jobs, list)

    def test_scrape_job_structure(self):
        scraper = LinkedInScraper()
        jobs = scraper.scrape_jobs('python developer', 'Netherlands')
        if jobs:  # May be empty if LinkedIn blocks
            job = jobs[0]
            assert 'title' in job
            assert 'company' in job
            assert 'location' in job
            assert 'url' in job
            assert 'source' in job
            assert job['source'] == 'linkedin'

    def test_deduplication(self):
        scraper = LinkedInScraper()
        jobs = scraper.scrape_jobs('python developer', 'Netherlands')
        keys = set()
        for job in jobs:
            key = f"{job['title']}|{job['company']}".lower()
            assert key not in keys, f"Duplicate found: {key}"
            keys.add(key)
