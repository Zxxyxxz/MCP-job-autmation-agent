# 🚀 Complete Setup Guide - Before Testing

## Current Status Check

✅ **Already Done:**
- GitHub account and authentication
- Git configured
- All project files present
- Database created (26 jobs)
- All Python packages installed

❌ **Still Needed:**
- Anthropic API key

---

## 🔑 Getting Your API Key (5 minutes)

### Step 1: Go to Anthropic Console
Open: https://console.anthropic.com/

### Step 2: Sign Up or Log In
- Use your email: bezekyigit0@gmail.com
- OR click "Sign in with Google" (faster)

### Step 3: Go to API Keys
- Click "API Keys" in left sidebar
- OR go to: https://console.anthropic.com/settings/keys

### Step 4: Create New Key
1. Click "Create Key" button
2. Name it: job-automation-agent
3. Click "Create Key"

### Step 5: Copy Your Key
**IMPORTANT:** Copy the key NOW! It looks like:
sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

You'll only see it once!

**Save it temporarily in:**
- Apple Notes, OR
- TextEdit, OR  
- Just keep the browser tab open

---

## 🔧 Setting the API Key

### Option A: Temporary (Recommended for Testing)

In your terminal, run:
export ANTHROPIC_API_KEY="paste-your-actual-key-here"

**Example:**
export ANTHROPIC_API_KEY="sk-ant-api03-abc123..."

**Pros:** Quick, easy, perfect for testing
**Cons:** Lost when you close terminal

### Option B: Permanent (Survives Restart)

In your terminal, run:
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc

**Pros:** Set once, always available
**Cons:** Stored in config file

---

## ✅ Verify Setup

After setting the key, verify:
echo $ANTHROPIC_API_KEY

Should show your key (starts with sk-ant-api03-)

---

## 🧪 Ready to Test!

Once your API key is set, run:
python3 test_full_pipeline.py

This will:
1. Scrape 25 jobs from LinkedIn
2. Analyze each with AI
3. Show top matches
4. Cost: ~$0.25

---

## 💰 About Costs

- Per job analysis: $0.01
- 25 jobs test: ~$0.25
- 100 jobs: $1-3

**Free credits:** Anthropic usually gives $5-10 free
That's 500-1,000 job analyses!

---

## ❓ FAQ

**Q: Do I need to update GitHub?**
A: No! GitHub is already set up and working.

**Q: Where does the API key go?**
A: In your terminal environment variable (not in any file)

**Q: Is the key committed to GitHub?**
A: No! It stays on your machine only.

**Q: What if I lose the key?**
A: Just create a new one in the Anthropic console

**Q: Can I test without the API key?**
A: Partially - scraper and database work, but AI analysis needs the key

---

## 🎯 Quick Start (After Getting Key)

# Set the key
export ANTHROPIC_API_KEY="your-key"

# Run the test
cd /Users/xxxyxxx/Desktop/job-agent/linkedin_pipeline
python3 test_full_pipeline.py

# View results
python3 view_dashboard.py

Done!
