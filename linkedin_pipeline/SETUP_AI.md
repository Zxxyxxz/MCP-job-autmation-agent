# AI Analyzer Setup Guide

## Step 1: Get Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with sk-ant-...)

## Step 2: Set API Key

### Option A: Temporary (for this terminal session)
export ANTHROPIC_API_KEY="your-api-key-here"

### Option B: Permanent (recommended)
Add to your shell profile (~/.zshrc or ~/.bash_profile):

echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc

## Step 3: Verify Setup

python3 analyzer_ai.py

This will run a test analysis on a sample job.

## Step 4: Full Integration Test

python3 test_full_pipeline.py

This will:
1. Scrape jobs from LinkedIn
2. Store them in database
3. Analyze each job with Claude AI
4. Generate match scores and reasoning
5. Store AI analysis in database
6. Show top matches

## API Costs

Claude API pricing (as of 2025):
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

Typical job analysis uses:
- ~1,500 input tokens (job + profile)
- ~500 output tokens (analysis)
- Cost per job: ~$0.01

Analyzing 100 jobs costs about $1.

## Next Steps

After setup:
1. Run test_full_pipeline.py to see everything working together
2. Customize analysis prompts in analyzer_ai.py
3. Add email monitoring (Day 5-7)
4. Add browser automation (Week 2)
