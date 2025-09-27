import re

test_response = '''SCORE: 85
STRENGTHS:
- Great Python skills
CONCERNS:
- Limited experience
FIT: Good match
RECOMMENDATION: Apply now'''

score = re.search(r'SCORE:\s*(\d+)', test_response, re.IGNORECASE)
print(f'Score: {score.group(1) if score else "FAIL"}')

strengths = re.search(r'STRENGTHS:(.*?)(?=CONCERNS:)', test_response, re.DOTALL)
if strengths:
    items = re.findall(r'-\s*(.+)', strengths.group(1))
    print(f'Strengths: {items}')

print('Regex test complete!')
