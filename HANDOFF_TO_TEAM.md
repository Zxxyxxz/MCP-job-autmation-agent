# Project Handoff Documentation - Job Search Automation Agent

**Date:** September 27, 2025  
**Current Status:** Day 4 Complete - Claude API Integration Working  
**Developer:** Yigit Bezek  
**Handoff Recipient:** Development Team

---

## 🚨 CRITICAL SECURITY NOTES

Before doing ANYTHING:

1. **DELETE** `linkedin_cookies.pkl` from both root and `linkedin_pipeline/` directories
2. **NEVER COMMIT** `.pkl` files to version control
3. Personal job search data is in `data/*.json` and `data/*.db` - do not share externally
4. API key is in environment variable `ANTHROPIC_API_KEY` - each dev needs their own

---

## Project Overview

An AI-powered job search automation agent that:
- Scrapes LinkedIn job postings
- Uses Claude API (Anthropic) for intelligent job matching
- Tracks applications in SQLite database  
- Generates personalized cover letters
- Eventually: Full automation with MCP tools (Gmail, Chrome, Calendar)

**Current State:** Core functionality working but inconsistent description fetching.

---

## What Has Been Completed (Days 1-4)

### ✅ Day 1-2: Basic Scraping Infrastructure
- LinkedIn public job scraper (`linkedin_pipeline/scrapers/linkedin_scraper.py`)
- BeautifulSoup-based scraping of job cards (title, company, location, URL)
- Does NOT fetch full descriptions - only metadata

### ✅ Day 3: Database Layer
- SQLite database (`linkedin_pipeline/database.py`)
- Tables: jobs, applications, tracking
- Methods: add_job, update_status, get_statistics
- **Location:** `linkedin_pipeline/data/jobs.db`

### ✅ Day 4: Claude AI Integration (PARTIALLY WORKING)
- `linkedin_pipeline/analyzer_ai.py` - Main AI analyzer
- Selenium-based description fetching with LinkedIn authentication
- Claude API integration for semantic job analysis
- Returns: score (0-100), fit_assessment, strengths, concerns, recommendation

**Working:** 4 out of 5 jobs analyzed successfully  
**Issue:** Description fetching inconsistent (304 chars vs 2500+ chars expected)

---

## File Structure Analysis

### MAIN PROJECT (linkedin_pipeline/)

```
linkedin_pipeline/
├── analyzer_ai.py              *** MAIN FILE - Current working version
├── database.py                 *** SQLite database interface
├── test_full_pipeline.py       *** Integration test (use this!)
├── yigit_profile.json          *** Candidate profile (customize per user)
│
├── scrapers/
│   └── linkedin_scraper.py     *** BeautifulSoup scraper (no auth)
│
├── analyzers/
│   └── job_analyzer.py         *** OLD VERSION - keyword-based scoring
│
├── data/                       *** SQLite DB + scraped jobs
│   ├── jobs.db
│   ├── linkedin_jobs_*.json
│   └── analyzed_*.json
│
├── config/
│   └── settings.json           *** Browser config, scoring weights
│
└── logs/
    └── scraper.log
```

### CLUTTER (Created During Debugging - Can Delete)

```
analyzer_ai.py.backup           Delete
analyzer_ai.py.broken           Delete  
analyzer_ai.py.before_selenium  Delete
analyzer_ai_updated.py          Delete
add_selenium_to_analyzer.py     Delete
debug_import.py                 Delete
fix_analyzer.py                 Delete
fix_analyzer.sh                 Delete
test_description.py             Delete
test_regex.py                   Delete
pre_test_check.py               Delete
```

### ROOT LEVEL (job-agent/)

```
linkedin_helper.py              *** Keep - Manual login tool
linkedin_cookies.pkl            *** DELETE IMMEDIATELY
test_selenium.py                Delete
linkedin_jobs.json              Personal data - don't commit
jobs_found.json                 Personal data - don't commit
job_scraper.py                  Old version - check if needed
yigit_profile.json              Keep
```

### OLD VERSIONS (Consider Archiving or Deleting)

```
archive_attempts/               Old scraping experiments
working_pipeline/               Duplicate files
job_analyzer_fixed_v3.py        Old version
job_analyzer_fixed_v4.py        Old version
```

---

## How The System Currently Works

### Flow Diagram

```
1. SCRAPING (linkedin_scraper.py)
   └─> Public LinkedIn search → Job cards (NO descriptions)
   └─> Saves: title, company, location, URL, job_id

2. DATABASE (database.py)
   └─> Stores jobs with status tracking
   └─> Status: scraped → ai_analyzed → applied → interview

3. AI ANALYSIS (analyzer_ai.py)
   ├─> Loads cookies (linkedin_cookies.pkl)
   ├─> Opens headless Chrome with Selenium
   ├─> Navigates to each job URL
   ├─> Clicks "See more" button
   ├─> Extracts full description (2000-5000 chars expected)
   ├─> Sends to Claude API with candidate profile
   └─> Returns: score, analysis, strengths, concerns

4. OUTPUT
   └─> Updates database with AI scores
   └─> Creates action plan markdown
```

### Critical Dependencies

1. **Selenium + ChromeDriver** - Auto-managed by Selenium 4.35.0
2. **Anthropic API** - Requires `ANTHROPIC_API_KEY` environment variable
3. **LinkedIn Cookies** - Each dev must generate their own via `linkedin_helper.py`

---

## Known Issues & Problems

### 🐛 Issue 1: Inconsistent Description Fetching (CRITICAL)

**Symptom:** Description lengths vary wildly:
- Job 1: 2,506 chars ✓ Good
- Job 2: 2,276 chars ✓ Good  
- Job 3: 3,465 chars ✓ Maybe extra UI text?
- Job 4: 304 chars ✗ FAILED (should be ~2000 chars)
- Job 5: 4,990 chars ✓ Good

**Root Cause:** CSS selectors in `get_full_description()` finding wrong elements or timing issues.

**Location:** `analyzer_ai.py`, lines ~90-140

**Current Selectors:**
```python
see_more_selectors = [
    "button[aria-label='Click to see more description']",
    "button[data-tracking-control-name='public_jobs_show-more-html-btn']",
    "button.show-more-less-html__button"
]

description_selectors = [
    "div.show-more-less-html__markup",
    "div.jobs-description__content",
    "div.description__text"
]
```

**Fix Needed:**
1. Increase wait time after click (currently 1s, try 3s)
2. Add explicit wait for description container to be present
3. Verify clicked button actually expanded content
4. Add fallback to scroll down entire page

### 🐛 Issue 2: Claude API Timeouts

**Symptom:** Job 4 timed out during analysis even though description was fetched.

**Error:** `Request timed out or interrupted`

**Cause:** Short descriptions or network issues

**Fix:** Add retry logic with exponential backoff

### 🐛 Issue 3: Headless Chrome May Fail

**Symptom:** LinkedIn detects automation and blocks requests.

**Current:** Runs in headless mode (`--headless` flag)

**Fix:** May need to run in non-headless mode or add more anti-detection

---

## What Still Needs To Be Done

### 📋 Phase 1: Stabilize Core (Priority: HIGH)

1. **Fix Description Fetching**
   - Test different selectors on 20+ real jobs
   - Add wait conditions and verification
   - Handle LinkedIn page variations

2. **Error Handling**
   - Retry logic for Claude API
   - Better cookie management
   - Graceful degradation if description unavailable

3. **Testing**
   - Create test suite for description fetching
   - Mock Claude API responses for unit tests
   - Integration tests for full pipeline

### 📋 Phase 2: Code Organization (Priority: MEDIUM)

1. **Cleanup**
   - Delete backup files (.backup, .broken)
   - Remove debug scripts
   - Archive old versions

2. **Refactoring**
   - Separate concerns (scraping vs analysis vs database)
   - Create proper package structure
   - Add type hints throughout

3. **Documentation**
   - API documentation for each module
   - Setup guide for new developers
   - Architecture diagram

### 📋 Phase 3: MCP Tool Integration (Priority: MEDIUM)

**Original Vision:** Full automation using MCP tools

1. **Gmail MCP**
   - Monitor application responses
   - Send follow-up emails
   - Track recruiter communications

2. **Chrome Control MCP**
   - Auto-fill application forms
   - Submit applications
   - Handle Easy Apply flows

3. **Calendar MCP**
   - Schedule interviews
   - Set reminders
   - Track application deadlines

4. **Apple Notes MCP**
   - Company research notes
   - Interview prep
   - Follow-up reminders

### 📋 Phase 4: Advanced Features (Priority: LOW)

1. **Cover Letter Generation** - Already coded but needs testing
2. **Resume Tailoring** - Generate job-specific resumes
3. **Follow-up System** - Auto-email after 7 days
4. **Analytics Dashboard** - Success rates, response times
5. **Multi-platform Support** - Indeed, Glassdoor, etc.

---

## How To Run This Project

### First-Time Setup (Each Developer)

1. **Clone and setup:**
```bash
cd /path/to/project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Get Anthropic API key:**
```bash
# Get from: https://console.anthropic.com/
export ANTHROPIC_API_KEY="your-key-here"
```

3. **Generate LinkedIn cookies:**
```bash
cd /path/to/project
python3 linkedin_helper.py
# Follow prompts to login manually
# Cookies saved to linkedin_cookies.pkl
```

4. **Move to project directory:**
```bash
cp linkedin_cookies.pkl linkedin_pipeline/
cd linkedin_pipeline
```

### Running the Full Pipeline

```bash
python3 test_full_pipeline.py
```

This will:
1. Scrape 25 jobs from LinkedIn
2. Add them to database
3. Analyze first 5 with Claude AI
4. Show top matches with scores

### Testing Individual Components

```bash
# Test scraper only
cd linkedin_pipeline
python3 scrapers/linkedin_scraper.py

# Test database
python3 database.py

# Test analyzer (needs jobs in DB)
python3 analyzer_ai.py
```

---

## Architecture Details

### Database Schema

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    title TEXT,
    company TEXT,
    url TEXT UNIQUE,
    location TEXT,
    description TEXT,
    scraped_date TIMESTAMP,
    status TEXT DEFAULT 'scraped',
    
    -- AI Analysis fields
    ai_score INTEGER,
    ai_match_reasoning TEXT,
    ai_strengths TEXT,  -- JSON array
    ai_concerns TEXT,   -- JSON array
    ai_recommendation TEXT,
    analyzed_at TIMESTAMP
);
```

### Claude API Integration

**Model:** `claude-sonnet-4-20250514`  
**Max Tokens:** 2000 for analysis, 1500 for cover letters

**Prompt Structure:**
```
JOB DETAILS:
Title: {job_title}
Company: {company}
Description: {description[:4000]}

CANDIDATE PROFILE:
{json.dumps(profile)}

Provide analysis in JSON format:
{
    "score": 0-100,
    "fit_assessment": "...",
    "strengths": [...],
    "concerns": [...],
    "recommendation": "..."
}
```

**Important:** Response must return `fit_assessment` (not `analysis`) to match database expectations.

### Selenium Configuration

```python
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # May need to disable
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

---

## Configuration Files

### yigit_profile.json

Contains candidate skills, experience, education. Customize for each user:

```json
{
    "name": "Yigit Bezek",
    "skills": {
        "languages": ["Python", "JavaScript", "TypeScript"],
        "frameworks": ["React", "PyTorch", "LangChain"],
        "tools": ["Git", "Docker", "AWS"]
    },
    "experience": [
        {
            "title": "AI Research Intern",
            "company": "PSA International",
            "description": "Multi-agent AI system using LangChain"
        }
    ]
}
```

### config/settings.json

Browser settings, scraping config, scoring weights:

```json
{
    "browser": {
        "user_agent": "...",
        "window_size": "1920,1080",
        "headless": true
    },
    "scoring": {
        "minimum_score": 60,
        "auto_apply_score": 80,
        "weights": {
            "skills_match": 0.4,
            "experience_level": 0.2,
            "location": 0.2,
            "visa_sponsorship": 0.2
        }
    }
}
```

---

## Testing Checklist for Team

1. [ ] Can you scrape jobs successfully?
2. [ ] Can you login and save cookies?
3. [ ] Does description fetching work on 10 different jobs?
4. [ ] Does Claude API analysis return valid JSON?
5. [ ] Is database properly storing all fields?
6. [ ] Can you run the full pipeline end-to-end?
7. [ ] Are there any crashes or errors in logs?

---

## Questions for Original Developer (Yigit)

1. What is the intended final use case? (Personal use or commercial?)
2. Is this for your own job search or to be shared?
3. Do you have access to LinkedIn Premium features?
4. What's the target deployment environment? (Local machine, server, Docker?)
5. Is there a deadline for completion?

---

## Recommended Next Steps

**Week 1:**
1. Clean up directory structure
2. Fix description fetching reliability
3. Add comprehensive error handling
4. Create proper test suite

**Week 2:**
1. Refactor code into proper modules
2. Add type hints and documentation
3. Implement retry logic
4. Test on 100+ real jobs

**Week 3:**
1. Begin MCP tool integration (Gmail first)
2. Create dashboard for tracking
3. Deploy to server (if needed)

---

## Contact & Support

**Original Developer:** Yigit Bezek  
**Project Start Date:** September 18, 2025  
**Current Phase:** MVP - Core functionality working  
**Repository:** [Add GitHub URL]  
**Documentation:** This file + inline code comments

---

**Last Updated:** September 27, 2025  
**Document Version:** 1.0
