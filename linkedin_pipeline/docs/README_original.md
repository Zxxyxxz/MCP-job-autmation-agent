# LinkedIn Job Application Pipeline

## Overview
Automated LinkedIn job search and analysis pipeline that:
- Scrapes public LinkedIn job listings
- Analyzes job descriptions against your profile
- Scores and prioritizes opportunities
- Creates actionable application plans

## Project Structure
```
linkedin_pipeline/
├── scrapers/           # Job scraping modules
│   └── linkedin_scraper.py
├── analyzers/          # Job analysis and scoring
│   └── job_analyzer.py
├── config/            # Configuration files
│   └── settings.json
├── data/              # Scraped and analyzed job data
├── logs/              # Application logs
├── run_pipeline.py    # Main orchestrator
└── yigit_profile.json # Your profile for matching
```

## Installation

1. Install dependencies:
```bash
pip install requests beautifulsoup4 selenium
```

2. Install ChromeDriver:
```bash
# On Mac with Homebrew:
brew install chromedriver
```

## Usage

### Quick Start
```bash
cd linkedin_pipeline
python run_pipeline.py
```

### Custom Search
```python
from scrapers.linkedin_scraper import LinkedInScraper

scraper = LinkedInScraper()
jobs = scraper.scrape_jobs(
    query="python developer",
    location="Amsterdam",
    time_filter="week"  # Options: 24h, week, month
)
```

### Analyze Existing Jobs
```python
from analyzers.job_analyzer import JobAnalyzer

analyzer = JobAnalyzer()
analyzer.analyze_jobs_file('data/linkedin_jobs_20250926.json')
```

## Configuration

Edit `config/settings.json` to customize:
- Search parameters (query, location, time filter)
- Scoring weights for job matching
- Browser settings (headless mode, user agent)
- Minimum scores for prioritization

## Scoring Algorithm

Jobs are scored on a 100-point scale based on:
- **Skills Match (40%)**: How many of your skills match the job
- **Experience Level (20%)**: Junior-friendly vs senior positions
- **Location (20%)**: Netherlands-based or remote opportunities
- **Visa Sponsorship (20%)**: International candidate friendliness

### Score Interpretation:
- **75-100**: High Priority - Apply immediately
- **60-74**: Medium Priority - Review and apply
- **Below 60**: Low Priority - Skip or apply if time permits

## Output Files

### Data Directory
- `linkedin_jobs_TIMESTAMP.json`: Raw scraped jobs
- `analyzed_TIMESTAMP.json`: Jobs with scores and analysis
- `ACTION_PLAN_DATE.md`: Prioritized application plan

### Logs Directory
- `scraper.log`: Scraping activity and errors
- `analyzer.log`: Analysis process and issues

## Troubleshooting

### Common Issues

1. **No jobs found**
   - Check internet connection
   - Try different search queries
   - LinkedIn may have updated their HTML structure

2. **Selenium errors**
   - Ensure ChromeDriver is installed and in PATH
   - Update ChromeDriver to match Chrome version
   - Check if Chrome browser is installed

3. **Rate limiting**
   - Increase wait times in settings.json
   - Use different search queries
   - Add proxy support (advanced)

## Next Steps

### Phase 1: Easy Apply Automation (TODO)
- Automate clicking "Easy Apply" button
- Fill in standard application fields
- Submit applications automatically

### Phase 2: Application Tracking (TODO)
- Track which jobs have been applied to
- Monitor application status
- Schedule follow-ups

### Phase 3: Multi-Platform Support (TODO)
- Add Indeed scraper (with better anti-bot handling)
- Add Glassdoor support
- Add AngelList/Wellfound for startups

## Version History

- v1.0 (2025-09-26): Initial LinkedIn scraper and analyzer
- v1.1 (planned): Add Easy Apply automation
- v2.0 (planned): Multi-platform support

## Notes

- The scraper uses public LinkedIn pages (no login required)
- Be respectful of rate limits to avoid being blocked
- Always review jobs before applying, even high-scored ones
- Keep your profile.json updated for better matching

## License

Private project - All rights reserved
