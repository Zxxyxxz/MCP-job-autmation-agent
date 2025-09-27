# Technical Specification - Job Search Automation Agent

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────┐
│              Job Search Agent System                │
└─────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
   │ SCRAPER │      │ ANALYZER│     │DATABASE │
   │LinkedIn │─────▶│ Claude  │────▶│ SQLite  │
   │BS4/HTTP │      │Selenium │     │  CRUD   │
   └─────────┘      └────┬────┘     └─────────┘
                         │
                    ┌────▼────┐
                    │  MCP    │
                    │ Tools   │
                    │(Future) │
                    └─────────┘
```

### Module Specifications

#### 1. LinkedIn Scraper (scrapers/linkedin_scraper.py)

**Purpose:** Fetch job listings from LinkedIn public search  
**Method:** BeautifulSoup + requests (no authentication required)  
**Limitations:** Cannot fetch full job descriptions

**Input:**
```python
query: str          # Search keywords
location: str       # Geographic location
time_filter: str    # '24h', 'week', 'month'
```

**Output:**
```python
{
    'title': str,
    'company': str,
    'location': str,
    'url': str,
    'job_id': str,
    'posted': str,
    'description': ''  # EMPTY - not fetched
}
```

**Performance:**
- Speed: ~25 jobs in 15 seconds
- Rate limit: None (public endpoint)
- Success rate: 95%+

**Known Issues:**
- LinkedIn changes CSS classes frequently
- No access to applicant count, salary, etc.

---

#### 2. AI Analyzer (analyzer_ai.py)

**Purpose:** Fetch full descriptions + Claude API analysis  
**Method:** Selenium + Anthropic Claude API

**Architecture:**

```python
class AIJobAnalyzer:
    def __init__(self):
        self.setup_driver()           # Chrome with anti-detection
        self.load_cookies()            # LinkedIn auth
        self.client = anthropic.Anthropic()
    
    def get_full_description(url):    # Selenium scraping
        # 1. Navigate to URL
        # 2. Click "See more" button
        # 3. Extract expanded description
        return description: str
    
    def analyze_job_fit(job):         # Claude API call
        # 1. Fetch description if missing
        # 2. Build prompt with profile
        # 3. Parse JSON response
        return {
            'score': int,
            'fit_assessment': str,
            'strengths': list,
            'concerns': list,
            'recommendation': str
        }
```

**Selenium Configuration:**
```python
ChromeOptions:
    --headless                          # Invisible browser
    --disable-blink-features            # Anti-detection
    --disable-gpu                       # Performance
    --no-sandbox                        # Compatibility
```

**Cookie Management:**
- Loads from `linkedin_cookies.pkl`
- Must be generated per developer
- Expires after ~30 days

**Claude API:**
- Model: claude-sonnet-4-20250514
- Max tokens: 2000
- Temperature: Default
- Cost: ~$0.003 per job

**Performance:**
- Speed: ~30 seconds per job (with description fetch)
- Success rate: 80% (4/5 working currently)
- Rate limits: 50 requests/minute (Claude API)

**Critical Bug:**
Description fetching returns inconsistent lengths:
- Expected: 2000-5000 characters
- Actual: 304-4990 characters

**Root Cause Analysis:**

```python
# Current implementation (line 90-140)
def get_full_description(self, job_url):
    self.driver.get(job_url)
    time.sleep(3)  # May be insufficient
    
    # Click see more - works
    button.click()
    time.sleep(1)  # TOO SHORT
    
    # Extract text - wrong selector?
    elem = self.driver.find_element(selector)
    return elem.text
```

**Issues:**
1. Wait time after click insufficient (1s → needs 3s)
2. No verification that content actually expanded
3. Selectors may match preview div instead of full content
4. No retry logic if first attempt fails

**Fix Required:**
```python
def get_full_description(self, job_url):
    self.driver.get(job_url)
    time.sleep(3)
    
    # Click and VERIFY expanded
    button = self.find_element(selector)
    initial_height = self.driver.execute_script("return document.body.scrollHeight")
    button.click()
    
    # Wait for height to change (proof of expansion)
    WebDriverWait(self.driver, 10).until(
        lambda d: d.execute_script("return document.body.scrollHeight") > initial_height
    )
    
    # Now extract
    elem = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )
    
    # Verify length
    text = elem.text
    if len(text) < 500:
        # Fallback: scroll and grab body
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        text = self.driver.find_element(By.TAG_NAME, "body").text
    
    return text
```

---

#### 3. Database Layer (database.py)

**Purpose:** Persist job data and tracking  
**Technology:** SQLite3  
**Location:** data/jobs.db

**Schema:**

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Job metadata (from scraper)
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    location TEXT,
    job_id TEXT,
    posted TEXT,
    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Full description (from analyzer)
    description TEXT,
    
    -- AI analysis results
    ai_score INTEGER,
    ai_match_reasoning TEXT,
    ai_strengths TEXT,  -- JSON array as string
    ai_concerns TEXT,   -- JSON array as string
    ai_recommendation TEXT,
    analyzed_at TIMESTAMP,
    
    -- Application tracking
    status TEXT DEFAULT 'scraped',
        -- Values: scraped → ai_analyzed → reviewed → 
        --         applied → interview → rejected/offer
    
    applied_date TIMESTAMP,
    response_date TIMESTAMP,
    interview_date TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_status ON jobs(status);
CREATE INDEX idx_ai_score ON jobs(ai_score DESC);
CREATE INDEX idx_scraped_date ON jobs(scraped_date DESC);
```

**API Methods:**

```python
class JobTracker:
    def add_job(job_data: dict) -> int:
        # Insert job, return id
        # Handles duplicates (url unique)
    
    def update_job(id: int, **fields) -> bool:
        # Update specific fields
    
    def update_status(id: int, status: str, notes: str) -> bool:
        # Change job status with timestamp
    
    def get_recent_jobs(limit: int = 20) -> List[dict]:
        # Latest scraped jobs
    
    def get_high_score_jobs(min_score: int = 70) -> List[dict]:
        # Jobs above threshold
    
    def get_statistics() -> dict:
        # Count by status, avg score, etc.
```

**Concurrency:** Single-threaded, no locking needed  
**Backups:** Manual (not automated)  
**Size:** ~1KB per job, ~1MB per 1000 jobs

---

### Data Flow Diagram

```
┌──────────────┐
│ User Request │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ test_full_pipeline.py                    │
│ 1. Scrape 25 jobs                        │
│ 2. Add to database                       │
│ 3. Analyze first 5                       │
└──────┬───────────────────────────────────┘
       │
       ├──────────▶ LinkedInScraper.scrape_jobs()
       │            └─▶ Returns: List[job_dict]
       │
       ├──────────▶ JobTracker.add_job()
       │            └─▶ SQLite INSERT
       │
       └──────────▶ AIJobAnalyzer.analyze_job_fit()
                    ├─▶ get_full_description()
                    │   └─▶ Selenium scraping
                    │
                    ├─▶ Claude API call
                    │   └─▶ JSON response
                    │
                    └─▶ JobTracker.update_job()
                        └─▶ SQLite UPDATE
```

---

## Testing Strategy

### Unit Tests (To Be Created)

**scrapers/test_linkedin_scraper.py**
```python
def test_scrape_jobs():
    scraper = LinkedInScraper()
    jobs = scraper.scrape_jobs("python", "Netherlands")
    assert len(jobs) > 0
    assert all('title' in j for j in jobs)

def test_url_parsing():
    # Test URL construction
    
def test_rate_limiting():
    # Verify delays between requests
```

**test_analyzer.py**
```python
def test_description_fetch():
    analyzer = AIJobAnalyzer()
    desc = analyzer.get_full_description(SAMPLE_URL)
    assert len(desc) > 1000
    assert "About the job" in desc

def test_claude_analysis():
    # Mock Claude API response
    # Verify JSON parsing
    
def test_cookie_loading():
    # Verify cookies are loaded correctly
```

**test_database.py**
```python
def test_add_job():
    tracker = JobTracker()
    job_id = tracker.add_job(SAMPLE_JOB)
    assert job_id > 0

def test_duplicate_handling():
    # Same URL should not create duplicate
```

### Integration Tests

**Current:** `test_full_pipeline.py` (manual execution)

**Should Add:**
- Automated test suite with pytest
- Mock external services (LinkedIn, Claude API)
- Test data fixtures
- CI/CD integration

### Performance Tests

**Metrics to track:**
- Time per job scraping
- Time per job analysis
- Claude API token usage
- Database query performance
- Memory usage over 1000 jobs

---

## Dependencies & Requirements

### Python Version
- Minimum: Python 3.9
- Tested: Python 3.12
- Recommended: Python 3.12+

### Core Dependencies

```txt
anthropic==0.39.0           # Claude API
selenium==4.35.0            # Browser automation
beautifulsoup4==4.12.3      # HTML parsing
requests==2.32.3            # HTTP client
```

### System Requirements

**For Scraping (BeautifulSoup):**
- Network connection
- No browser required

**For Analysis (Selenium):**
- Chrome/Chromium browser
- ChromeDriver (auto-managed by Selenium 4+)
- 2GB RAM minimum
- 500MB disk space

**For Claude API:**
- API key from anthropic.com
- Network connection
- Budget: ~$0.003 per job analyzed

---

## Error Handling

### Current State: MINIMAL

Most errors are logged but not recovered from.

**Needs Implementation:**

```python
class RetryableError(Exception):
    """Error that should be retried"""

def analyze_with_retry(job, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return analyze_job_fit(job)
        except TimeoutError:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
        except ValueError:  # JSON parse error
            # Log and skip
            return default_analysis()
```

---

## Security Considerations

### Credentials Management

**Current Issues:**
- LinkedIn cookies stored as pickle file (insecure)
- API key in environment variable (acceptable)
- No encryption at rest

**Should Implement:**
- Encrypted cookie storage
- Key rotation mechanism
- Secure credential vault (e.g., keyring)

### Data Privacy

**Personal Information Stored:**
- Job search history
- Company preferences
- Application outcomes

**Recommendations:**
- Add data retention policy
- Implement data export feature
- Allow selective deletion

### Rate Limiting

**Current:**
- No rate limiting on scraper (risky)
- Claude API has built-in limits

**Should Add:**
- Configurable delays between requests
- Exponential backoff on failures
- Respect robots.txt

---

## Deployment Considerations

### Current: Local Machine Only

**Requirements for Production:**

1. **Containerization:**
```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    chromium chromium-driver
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY linkedin_pipeline/ /app/
WORKDIR /app
CMD ["python", "run_pipeline.py"]
```

2. **Scheduling:**
- Cron job for daily scraping
- Queue system for analysis (RabbitMQ, Celery)

3. **Monitoring:**
- Logging to centralized system (Splunk, CloudWatch)
- Alerting on failures
- Performance metrics

4. **Scaling:**
- Multiple Selenium instances
- Load balancing for Claude API
- Database connection pooling

---

## Code Quality Issues

### Current State: PROTOTYPE QUALITY

**Problems:**
1. No type hints
2. Inconsistent naming conventions
3. Magic numbers/strings
4. Tight coupling between modules
5. No input validation
6. Minimal error handling

**Refactoring Needed:**

```python
# Current (bad)
def analyze(job):
    desc = get_desc(job['url'])
    score = claude(desc)
    return score

# Should Be (good)
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class JobAnalysis:
    score: int
    assessment: str
    strengths: list[str]
    concerns: list[str]

def analyze_job(
    job: Dict[str, str],
    max_retries: int = 3
) -> Optional[JobAnalysis]:
    """
    Analyze a job posting using Claude AI.
    
    Args:
        job: Job dict containing 'url' and 'title'
        max_retries: Number of retry attempts
    
    Returns:
        JobAnalysis object or None if analysis fails
        
    Raises:
        ValueError: If job dict is invalid
    """
    if not job.get('url'):
        raise ValueError("Job must have URL")
    
    description = fetch_description(job['url'])
    if not description:
        return None
    
    analysis = call_claude_api(description, retries=max_retries)
    return JobAnalysis(**analysis)
```

---

## Future Enhancements

### Phase 1: Stabilization (Weeks 1-2)
- [ ] Fix description fetching reliability
- [ ] Add comprehensive test suite
- [ ] Implement proper error handling
- [ ] Add logging and monitoring

### Phase 2: Features (Weeks 3-4)
- [ ] Cover letter generation (exists but untested)
- [ ] Resume tailoring
- [ ] Email integration (Gmail MCP)
- [ ] Calendar integration (scheduling)

### Phase 3: Automation (Weeks 5-6)
- [ ] Auto-apply to Easy Apply jobs
- [ ] Automated follow-ups
- [ ] Interview scheduling
- [ ] Response tracking

### Phase 4: Scale (Weeks 7-8)
- [ ] Multi-platform support (Indeed, Glassdoor)
- [ ] Analytics dashboard
- [ ] A/B testing of cover letters
- [ ] Machine learning for optimization

---

## Critical Decisions Needed

1. **Deployment Environment**
   - Local machine only?
   - Cloud server (AWS, GCP)?
   - Docker container?

2. **Data Retention**
   - How long to keep job history?
   - GDPR compliance needed?

3. **Access Control**
   - Single user or multi-user?
   - Role-based access?

4. **Budget**
   - Claude API costs at scale
   - Server costs if deployed
   - ChromeDriver licensing

5. **Legal**
   - LinkedIn ToS compliance
   - Scraping legality
   - Data protection laws

---

## Performance Benchmarks

### Current Performance (Local Machine)

**Scraping:**
- 25 jobs: 15 seconds
- Throughput: 100 jobs/minute

**Analysis:**
- Per job: 30 seconds (20s wait + 10s Claude)
- Throughput: 2 jobs/minute

**Database:**
- Insert: <1ms
- Query: <10ms
- No performance issues observed

### Optimization Opportunities

1. **Parallel Processing**
   - Current: Sequential (1 job at a time)
   - Potential: 10 concurrent Selenium instances
   - Speedup: 10x

2. **Description Caching**
   - Many jobs link to same URL
   - Cache descriptions by URL
   - Saves ~50% fetch time

3. **Batch Claude API**
   - Current: 1 job per request
   - Potential: 5 jobs per request (prompt batching)
   - Saves API calls

---

**Document Version:** 1.0  
**Last Updated:** September 27, 2025  
**Maintainer:** Development Team
