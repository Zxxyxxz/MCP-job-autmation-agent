# 📺 What To Expect - Command by Command

## 🔧 SETTING THE API KEY

### Command:
export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key"

### What Happens:
- No output (silent success)
- Key is now in your terminal session
- Lasts until you close the terminal

### Verify it worked:
echo $ANTHROPIC_API_KEY

**Expected Output:**
sk-ant-api03-xxxxxxxxxxxxxxxxx... (your full key)

**If empty:** Key not set, try again

---

## 🧪 RUNNING THE TEST

### Command:
python3 test_full_pipeline.py

### What You'll See:

**Phase 1: Initialization (2 seconds)**
============================================================
🚀 COMPLETE JOB PIPELINE TEST
============================================================

📦 Step 1: Initializing components...
✅ Database tables created successfully!
✅ AI Analyzer initialized with Claude API
✅ All components initialized

**Phase 2: Scraping (10-20 seconds)**
🔍 Step 2: Scraping jobs from LinkedIn...

🔍 Searching LinkedIn: python developer OR machine learning engineer in Netherlands (past week)
✅ Found 60 job listings
  ✓ Python Engineer... at Datenna
  ✓ Backend Developer... at Booking.com
  ✓ ML Engineer... at TomTom
  [... more jobs ...]

💾 Saved 25 jobs to data/linkedin_jobs_20250926_151234.json
✅ Found 25 jobs

**Phase 3: Database (1 second)**
💾 Step 3: Adding jobs to database...
  ✓ Added: Python Engineer at Datenna (ID: 27)
  ✓ Added: Backend Developer at Booking.com (ID: 28)
  [... 23 more ...]
✅ Added 25 new jobs

**Phase 4: AI Analysis (2-3 minutes)** ⏰ TAKES TIME
🤖 Step 4: Analyzing jobs with Claude AI...
(This may take a minute...)

  [1/5] Analyzing: Python Engineer at Datenna

🤖 Analyzing: Python Engineer at Datenna...
    ✓ Score: 82/100

  [2/5] Analyzing: Backend Developer at Booking.com

🤖 Analyzing: Backend Developer at Booking.com...
    ✓ Score: 78/100

  [3/5] Analyzing: ML Engineer at TomTom...
    ✓ Score: 85/100

  [4/5] Analyzing: Full Stack Engineer at Salento...
    ✓ Score: 72/100

  [5/5] Analyzing: Junior Python Developer at HCLTech...
    ✓ Score: 88/100

✅ Analyzed 5 jobs

**Phase 5: Results (2 seconds)**
============================================================
🎯 TOP MATCHES
============================================================

1. Junior Python Developer at HCLTech
   Score: 88/100 | Location: Amsterdam Area
   URL: https://linkedin.com/jobs/view/3845...

   Why its a good fit:
   Strong match due to Python expertise and ML background. The junior
   level aligns perfectly with your recent graduation. Location in
   Amsterdam is ideal for your visa situation...

   Top Strengths:
   • AI Facility Layout Optimizer thesis demonstrates advanced Python
     and optimization skills directly applicable to this role
   • Multi-agent system experience at PSA International shows ability
     to work on complex, production-scale projects

2. ML Engineer at TomTom
   [similar details...]

3. Python Engineer at Datenna
   [similar details...]

**Phase 6: Statistics**
============================================================
📊 DATABASE STATISTICS
============================================================

Total jobs in database: 51
Average AI score: 78.6/100

Jobs by status:
  • scraped: 46
  • ai_analyzed: 5

============================================================
✅ PIPELINE TEST COMPLETE!
============================================================

📋 What you can do now:

1. View all jobs:
   python3 view_dashboard.py

2. View high-scoring jobs:
   [command shown...]

3. Generate cover letter for top job:
   python3 generate_cover_letter.py

---

## 📊 VIEWING DASHBOARD

### Command:
python3 view_dashboard.py

### What You'll See:

============================================================
                     📊 JOB DASHBOARD
============================================================

📈 Overview:
   Total jobs: 51
   Applications sent: 0
   Interviews: 0
   Average AI score: 78.6/100
   Response rate: 0%

📋 Jobs by Status:
   scraped                   46 jobs
   ai_analyzed                5 jobs

🎯 Top 10 Jobs (by AI score):

   1. [88/100] Junior Python Developer
      Company: HCLTech                     Status: ai_analyzed
      Location: Amsterdam                  ID: 31

   2. [85/100] ML Engineer
      Company: TomTom                      Status: ai_analyzed
      Location: Amsterdam                  ID: 29

   [... 8 more ...]

🔔 Jobs Needing Follow-up:
   None (or no applications sent yet)

🕐 Recent Jobs (Last 5):
   • Junior Python Developer at HCLTech
     Scraped: 2025-09-26 | Status: ai_analyzed
   [... 4 more ...]

============================================================

💡 Quick Commands:
   [helpful commands shown...]

============================================================

---

## ✍️ GENERATING COVER LETTER

### Command:
python3 generate_cover_letter.py

### What You'll See:

📋 High-scoring jobs in database:

1. [88/100] Junior Python Developer at HCLTech
   ID: 31 | Amsterdam

2. [85/100] ML Engineer at TomTom
   ID: 29 | Amsterdam

3. [82/100] Python Engineer at Datenna
   ID: 27 | Amsterdam Area

Usage: python3 generate_cover_letter.py <job_id>
Example: python3 generate_cover_letter.py 31

### Then run:
python3 generate_cover_letter.py 31

### What You'll See:

📄 Generating cover letter for:

   Junior Python Developer at HCLTech
   Score: 88/100

✍️  Generating cover letter for HCLTech...
  ✓ Generated 847 character cover letter

✅ Cover letter saved to: data/cover_letter_HCLTech_31.txt

📄 Preview:
============================================================
I am excited to apply for the Junior Python Developer position
at HCLTech. As a recent Creative Technology graduate from the
University of Twente with hands-on AI/ML experience, I am
particularly drawn to this opportunity to contribute to your
team's innovative projects.

During my thesis, I developed an AI Facility Layout Optimizer
using genetic algorithms that achieved a 20% throughput
improvement, demonstrating my ability to apply machine learning
to real-world optimization problems...
============================================================

✅ Database updated!

---

## 💰 COST TRACKING

After the test run, you can check costs:

**API Usage:**
- 5 jobs analyzed: 5 × $0.01 = ~$0.05
- 1 cover letter: $0.02
- **Total: ~$0.07**

**Your free credits:** Usually $5-10
**Remaining:** ~$4.93-9.93 (700-1,400 more analyses!)

---

## ❌ COMMON ERRORS & FIXES

### Error: "ANTHROPIC_API_KEY not set"
**Fix:** Run export ANTHROPIC_API_KEY="your-key"

### Error: "Invalid API key"
**Fix:** Check key starts with sk-ant-api03-

### Error: "Module not found: anthropic"
**Fix:** pip3 install anthropic

### Error: "No jobs found"
**Fix:** Check internet connection, LinkedIn might be rate-limiting

### Error: "Database locked"
**Fix:** Close other programs using the database

---

## ✅ SUCCESS INDICATORS

You'll know it worked when you see:
1. ✅ "AI Analyzer initialized with Claude API"
2. ✅ Jobs scraped (25 found)
3. ✅ Jobs added to database
4. ✅ AI analysis completes without errors
5. ✅ Top matches shown with scores
6. ✅ No error messages

---

## 🎯 WHAT TO DO AFTER TESTING

1. **View your results:**
   - Dashboard: python3 view_dashboard.py
   - Cover letters: ls data/cover_letter_*

2. **Apply to top matches:**
   - Open the URLs from top matches
   - Use generated cover letters
   - Track applications in database

3. **Continue job search:**
   - Run test_full_pipeline.py daily
   - Adjust search queries in config/settings.json
   - Monitor response rates

4. **Next features:**
   - Email monitoring (Week 1, Day 5-7)
   - Browser automation (Week 2)
   - Application tracking
