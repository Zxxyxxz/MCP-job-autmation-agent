#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from analyzers.analyzer_ai import AIJobAnalyzer

# Test with a job that has a description
test_job = {
    'title': 'Python Developer',
    'company': 'Test Company',
    'location': 'Amsterdam',
    'description': """
    We are looking for a Python developer with 2+ years experience.
    Requirements:
    - Python, Django, Flask
    - PostgreSQL
    - Docker experience
    - Team player
    
    We offer competitive salary and visa sponsorship.
    """
}

analyzer = AIJobAnalyzer()
result = analyzer.analyze_job_fit(test_job)

print(f"Score: {result['score']}/100")
print(f"Strengths: {len(result['strengths'])} items")
print(f"Concerns: {len(result['concerns'])} items")
print(f"Has fit assessment: {bool(result['fit_assessment'])}")
print(f"Has recommendation: {bool(result['recommendation'])}")

if result['score'] > 0:
    print("\n✅ Parser is working!")
else:
    print("\n❌ Parser still broken. Check raw response:")
    print(result['raw_response'][:500])
