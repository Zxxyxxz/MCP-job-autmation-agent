# Job-Agent: AI-Powered LinkedIn Job Search & Auto-Apply Platform

## Project Overview

AI-powered LinkedIn job automation platform built for Yigit Bezek (BSc Creative Technology, University of Twente 2025, orientation year visa in Netherlands valid until 2026). The system scrapes LinkedIn job postings, enriches them with full descriptions via headless Chrome, analyzes candidate fit using Claude AI, generates PDF cover letters, and can auto-apply to jobs through LinkedIn Easy Apply and external career sites.

**Tech stack:** Python 3.12+, BeautifulSoup4, Selenium (headless Chrome), Anthropic Claude API, SQLite, Streamlit, ReportLab, Folium

**Status:** Pipeline works end-to-end. Auto-apply system is built but needs testing and hardening (see "Auto-Apply Status" section). 36 unit tests + 8 integration tests passing (53 total).

---

## Quick Reference Commands

```bash
# All commands run from linkedin_pipeline/
cd linkedin_pipeline

# Full pipeline (headless, no focus stealing)
python main.py                                    # Full pipeline with defaults
python main.py scrape -q "AI engineer"            # Scrape only
python main.py enrich --limit 10                  # Enrich 10 jobs
python main.py analyze --limit 20                 # Analyze 20 jobs
python main.py --no-headless                      # Show browser for debugging

# Web UI
streamlit run ui/app.py                           # Web UI at localhost:8501

# Tests
pytest tests/                                     # All 53 tests
pytest tests/unit/ -v                             # 36 unit tests

# Utilities
python src/utils/view_dashboard.py                # Terminal dashboard
python src/analyzers/generate_cover_letter.py 5   # Cover letter for job ID 5
```

**Prerequisites:**
- `export ANTHROPIC_API_KEY="sk-ant-..."` (required for AI analysis and cover letters)
- Chrome browser installed (Selenium uses ChromeDriver via webdriver-manager)
- `config/linkedin_cookies.pkl` for authenticated LinkedIn scraping (optional - detection works without login)
- `pip install -r requirements.txt`

---

## Architecture & Data Flow

```
LinkedIn Public Pages (HTML)
         |
    [1] LinkedInScraper (BS4 + requests)
         |  Extracts: title, company, location, URL
         |  Dedup: title|company key, max 20 per page
         v
    [2] SmartDescriptionEnricher (headless Selenium)
         |  Single reusable driver (no focus stealing)
         |  Anti-detection: CDP commands, custom UA, random delays
         |  Multiple CSS selector strategies, 500-char quality threshold
         v
    [3] ValidatedEnricher (Selenium)
         |  Quality score 0-100, language detection (english/dutch/mixed)
         |  Degree requirement extraction, experience years parsing
         v
    [4] AIJobAnalyzer (Claude API)
         |  Pre-qualification: checks degree, experience, language
         |  Model: claude-sonnet-4-20250514, temp=0.3
         |  Prompt -> SCORE/STRENGTHS/CONCERNS/FIT/RECOMMENDATION
         v
    [5] ApplyLinkExtractor (headless Selenium)
         |  Detects: EASY_APPLY vs EXTERNAL (company career site)
         |  Uses LinkedIn page source tracking data (works without login)
         v
    [6] Auto-Apply System
         |  LinkedInEasyApply: modal form filling, CV upload, submit
         |  ExternalSiteApplier: generic HTML form filling for career sites
         |  AIFormFiller: answers questions from profile + Claude
         |  CoverLetterPDF: generates styled PDF cover letters
         v
    [7] Database (SQLite) + Streamlit UI
         Full lifecycle tracking, analytics, map visualization
```

---

## Directory Structure

```
job-agent/                              # Project root
  CLAUDE.md                             # THIS FILE - project documentation
  linkedin_pipeline/                    # *** MAIN PROJECT DIRECTORY ***
    main.py                             # CLI entry point (argparse)
    requirements.txt                    # Python dependencies

    config/
      yigit_profile.json               # Candidate profile (278 lines, PII inside)
      settings.json                    # Search params, browser config (headless=true)
      cv.pdf                           # Candidate CV for auto-apply uploads
      linkedin_cookies.pkl             # LinkedIn auth cookies (NEVER commit)

    src/
      run_pipeline.py                  # JobPipeline: unified scrape -> enrich -> analyze -> report

      scrapers/
        linkedin_scraper.py            # LinkedInScraper: BS4 public page scraper
        smart_description_enricher.py  # SmartDescriptionEnricher: headless, driver reuse, retry
        validated_enricher.py          # ValidatedEnricher: quality checks, language detection
        apply_link_extractor.py        # ApplyLinkExtractor: EASY_APPLY vs EXTERNAL detection

      analyzers/
        analyzer_ai.py                 # AIJobAnalyzer: Claude analysis, scoring, cover letters
        generate_cover_letter.py       # CLI tool: generate cover letter for a job ID

      auto_apply/                      # *** AUTO-APPLY SYSTEM (needs hardening) ***
        __init__.py                    # Exports: CoverLetterPDF, LinkedInEasyApply, AIFormFiller, ExternalSiteApplier
        linkedin_easy_apply.py         # LinkedInEasyApply: Easy Apply modal automation
        external_site_applier.py       # ExternalSiteApplier: generic career site form filler
        form_filler.py                 # AIFormFiller: AI-powered question answering
        pdf_cover_letter.py            # CoverLetterPDF: ReportLab PDF generation

      database/
        database.py                    # JobDatabase: unified, thread-safe, 5 tables

      utils/
        view_dashboard.py              # Terminal-based dashboard

    ui/
      app.py                           # Streamlit app: 6 tabs, non-blocking operations
      background_analyzer.py           # BackgroundAnalyzer: threaded AI analysis
      background_applier.py            # BackgroundApplier: threaded detection, enrichment, auto-apply
      netherlands_map.py               # Folium map with Dutch cities

    tests/
      conftest.py                      # Shared fixtures (tmp_db_path, sample_job, sample_analysis)
      unit/
        test_database.py               # 18 tests: CRUD, status, analysis, interviews, search
        test_description.py            # 9 tests: language detection, experience extraction, quality
        test_regex.py                  # 4 tests: Claude response parsing
        test_scraper.py                # 5 tests: scraper init, structure, dedup
      integration/
        test_all_components.py         # Module imports, config loading
        test_database_integration.py   # Scraper -> DB integration
        test_full_pipeline.py          # End-to-end: scrape -> DB -> AI analysis

    data/                              # SQLite DB + scraped JSON (gitignored)
    logs/                              # Application logs (gitignored)
```

---

## Core Components

### Scrapers (`src/scrapers/`)

**LinkedInScraper** - BS4-based public page scraper. No auth needed. Returns `[{title, company, location, url, description:'', source, scraped_at}]`.

**SmartDescriptionEnricher** - Headless Selenium with single reusable driver (no focus stealing). Anti-detection: CDP commands, custom UA, random delays. Creates driver once, reuses across all jobs, closes when done. Context manager support (`with SmartDescriptionEnricher() as e:`).

**ValidatedEnricher** - Quality checks on fetched descriptions. Language detection (counts Dutch word occurrences, thresholds: >15=dutch, >5=mixed). Degree/experience extraction via regex.

**ApplyLinkExtractor** - Detects whether a LinkedIn job uses Easy Apply or external career site. **Key insight:** Works without being logged in by checking LinkedIn's page source for tracking data attributes (`apply-link-onsite` = Easy Apply, `apply-link-offsite` = External). Reusable headless driver with context manager support.

### Analyzers (`src/analyzers/`)

**AIJobAnalyzer** - Claude API for job fit analysis (temp=0.3, max_tokens=2000) and cover letter generation (temp=0.7). Pre-qualification checks degree/experience/language before API call. Disqualified jobs get score=20, skip API. Scoring: 80+ = high priority, 70-79 = good, 60-69 = decent, <60 = low.

### Auto-Apply System (`src/auto_apply/`) - NEEDS WORK

**LinkedInEasyApply** - Automates the LinkedIn Easy Apply modal flow:
1. Clicks Easy Apply button on job page
2. Processes multi-step modal (Next -> Review -> Submit)
3. Fills text inputs, textareas, dropdowns, radio buttons, checkboxes
4. Uploads CV (`config/cv.pdf`) and cover letter PDF
5. Uses AIFormFiller for intelligent question answering
- **Current status:** Built and structured but NEEDS TESTING. The LinkedIn cookies are expired, which means the Easy Apply flow requires re-authentication. The modal detection selectors may need updating for current LinkedIn HTML.

**ExternalSiteApplier** - Generic career site form filler for Greenhouse, Lever, Workday, SmartRecruiters, etc.:
1. Navigates to external career URL
2. Detects ATS platform from URL patterns
3. Handles iframes (common on Greenhouse/Workday)
4. Fills all form fields: text, email, phone, textarea, select, file upload, checkboxes
5. Finds and clicks submit button
- **Current status:** Built but UNTESTED on real career sites. Needs real-world testing and hardening.

**AIFormFiller** - Answers application questions intelligently:
- 40+ regex patterns for instant answers (visa, salary, experience, languages, personal info)
- Claude API fallback (temp=0.3) for complex questions
- Dropdown option matching (picks best option from available choices)
- All answers sourced from `config/yigit_profile.json`

**CoverLetterPDF** - Generates styled A4 PDF cover letters via ReportLab:
- Header: name, contact, portfolio
- Accent line, date, recipient, subject
- Justified body paragraphs
- Signature block
- Saves to `data/cover_letters/`

### Database (`src/database/`)

**JobDatabase** - Thread-safe SQLite with 5 tables, advanced deduplication, auto-migration, context manager. `JobTracker` alias for backward compat.

### UI (`ui/`)

**Streamlit app** with 6 tabs: Top Matches, All Jobs, Applications, AI Chat, Analytics, Location Map.

Key UI features:
- **Non-blocking operations**: enrichment, analysis, detection, auto-apply all run in background threads
- **BackgroundApplier**: manages threaded operations with status tracking
- **Detect All**: batch-detects apply methods for all visible jobs
- **PDF cover letter** generation + download
- **Auto Apply** buttons for Easy Apply and External sites
- No `time.sleep()` polling loops (user clicks Refresh to update)

---

## Auto-Apply Status & What Needs Work

### What Works
1. Apply method detection (EASY_APPLY vs EXTERNAL) - tested, reliable
2. PDF cover letter generation - tested, produces clean PDFs
3. AIFormFiller pattern matching - tested for common questions
4. Background threading for all operations - no UI freezing

### What Needs Testing & Hardening

**Priority 1: LinkedIn Easy Apply**
- LinkedIn cookies need to be refreshed (current ones are expired - `li_at` not present)
- To refresh: log into LinkedIn in Chrome, export cookies to `config/linkedin_cookies.pkl`
- The Easy Apply modal detection uses selectors like `div.jobs-easy-apply-modal`, `div[role="dialog"]` - these may need updating
- Test the full flow: click Easy Apply -> fill forms -> upload CV -> submit
- Key file: `src/auto_apply/linkedin_easy_apply.py`

**Priority 2: External Career Site Apply**
- COMPLETELY UNTESTED on real career sites
- The generic HTML form parser finds fields by `input[type]`, `select`, `textarea`, `input[type="file"]`
- Label extraction uses 8 strategies: aria-label, label[for], placeholder, name, data attributes, parent label, sibling label
- ATS detection covers: Greenhouse, Lever, Workday, SmartRecruiters, Ashby, BambooHR, Recruitee, Personio
- Iframe handling for Greenhouse/Workday
- Submit button detection searches for common button texts in English and Dutch
- Key file: `src/auto_apply/external_site_applier.py`

**Priority 3: Improvements to Consider**
- Screenshot + Claude Vision for forms the parser can't handle
- CAPTCHA detection and notification (don't try to solve, just alert user)
- Form validation error detection (re-read page after submit, check for error messages)
- Multi-page application forms (some external sites have 3-5 steps)
- "Review before submit" mode - fill everything but pause before clicking submit
- Better logging of what was filled and what was skipped (for debugging)
- LinkedIn cookie auto-refresh (log in via Selenium, save cookies)

---

## Configuration Files

**`config/settings.json`** - Search and browser settings
- `search_settings`: default query, location (Netherlands), time_filter (week), max 25 per search
- `browser`: headless=true (default), window_size 1920x1080
- `scoring`: minimum_score 60, auto_apply_score 75

**`config/yigit_profile.json`** (278 lines) - Candidate profile used by AIFormFiller
- Personal: name, email, phone, visa status, portfolio, linkedin, github
- Education: BSc Creative Technology, University of Twente 2025
- Work experience: PSA International (2024), Homemade B.V. (2023-2024), etc.
- Technical skills: Python expert, JavaScript proficient, PyTorch/LangChain/OpenCV
- Languages: Turkish native, English fluent, Dutch A2
- Preferences: target roles, locations, salary 45-50k EUR

**`config/cv.pdf`** - Candidate CV uploaded during auto-apply

---

## Database Schema

```sql
-- jobs: 40+ columns
id, job_id, title, company, location, url, description, source, job_hash
status (new -> applied -> interview_scheduled -> offer/rejection)
ai_score, ai_strengths (JSON), ai_concerns (JSON), ai_fit_assessment, ai_recommendation
disqualified, disqualification_reasons (JSON)
application_link (EASY_APPLY | external_url | NULL)
application_method (auto_easy_apply | auto_external | manual)
cover_letter, applied_at, enriched_at, analyzed_at
-- Plus: application_history, emails, email_tracking, interviews tables
```

---

## Security

- **`config/linkedin_cookies.pkl`** - Session cookies. In `.gitignore`. NEVER commit.
- **`config/yigit_profile.json`** - Contains PII (email, phone). Review before committing.
- **`config/cv.pdf`** - Personal CV. In `.gitignore`.
- **`ANTHROPIC_API_KEY`** - Environment variable only, never hardcoded.
- **`data/`** - All `.db` and `.json` files gitignored.

---

## Testing

```bash
pytest tests/ -v              # All 53 tests (36 unit + 17 integration)
pytest tests/unit/ -v         # Fast unit tests only
pytest tests/integration/ -v  # Integration tests (some hit LinkedIn)
```

All tests use proper pytest fixtures. Integration tests that need API key are skipped with `@pytest.mark.skipif`.

---

## Key Design Decisions

1. **Headless by default** - Chrome runs in background, never steals focus. `--no-headless` flag for debugging.
2. **Driver reuse** - SmartDescriptionEnricher and ApplyLinkExtractor create one Chrome instance and reuse across all jobs. Context manager closes when done.
3. **Non-blocking UI** - All Selenium/API operations run in background threads (BackgroundApplier, BackgroundAnalyzer). UI stays responsive.
4. **Unauthenticated detection** - ApplyLinkExtractor detects Easy Apply vs External by checking page source for LinkedIn's tracking data attributes, not button text. Works without cookies.
5. **AI form filling** - 40+ regex patterns for instant answers, Claude API fallback for complex questions. Profile-driven answers.
6. **PDF cover letters** - ReportLab generates A4 PDFs with professional styling. Downloaded and uploaded during auto-apply.
