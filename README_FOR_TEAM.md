# Job Search Automation Agent - Quick Start

## Critical Security Warning

**BEFORE SHARING THIS DIRECTORY:**

1. Delete `linkedin_cookies.pkl` - it contains your LinkedIn session
2. Delete `data/jobs.db` - it contains your personal job search history  
3. Delete `data/*.json` - these are your scraped jobs

```bash
rm linkedin_cookies.pkl
rm linkedin_pipeline/linkedin_cookies.pkl
rm linkedin_pipeline/data/*.db
rm linkedin_pipeline/data/*.json
```

## Quick Start for New Developers

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set API key: `export ANTHROPIC_API_KEY="your-key"`
4. Generate YOUR OWN cookies: `python3 linkedin_helper.py`
5. Run pipeline: `cd linkedin_pipeline && python3 test_full_pipeline.py`

## Documentation

See the following files for details:
- `HANDOFF_TO_TEAM.md` - Complete project handoff documentation
- `TECHNICAL_SPEC.md` - Technical specifications and architecture

## Current Status

Working: Scraper + Database + Claude API (80% success rate)  
Not Working: Description fetching is inconsistent (see TECHNICAL_SPEC.md)

## Key Files

- `linkedin_pipeline/analyzer_ai.py` - Main AI analyzer (working)
- `linkedin_pipeline/database.py` - SQLite interface (working)
- `linkedin_pipeline/test_full_pipeline.py` - Integration test (use this)
- `linkedin_pipeline/scrapers/linkedin_scraper.py` - Job scraper (working)

## Files to Delete Before Sharing

These are backup/debug files created during development:

```bash
cd linkedin_pipeline
rm -f *.backup *.broken *.before_selenium
rm -f add_selenium_to_analyzer.py debug_import.py
rm -f fix_analyzer.py fix_analyzer.sh
rm -f test_description.py test_regex.py
```

## Questions?

Contact original developer: Yigit Bezek
