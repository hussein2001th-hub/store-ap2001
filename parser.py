import json
import os

path = r'C:\Users\حسين\.gemini\antigravity\brain\b6087634-64da-4015-b29d-97074e858c8c\.system_generated\steps\656\content.md'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

if text.startswith('```'):
    lines = text.split('\n')
    text = '\n'.join(lines[1:-1])

services = json.loads(text)

insta_foll = [s for s in services if 'instagram' in s.get('category', '').lower() and 'follower' in s.get('name', '').lower()]
insta_foll.sort(key=lambda x: float(x.get('rate', 999)))

print('=== Best Guaranteed Followers ===')
guaranteed = [s for s in insta_foll if '365' in s['name'] or '30 days' in s['name'].lower() or 'refill' in s['name'].lower()]
for s in guaranteed[:3]:
    print('ID:', s['service'], '| Price: $', s['rate'], '| Min:', s['min'], '| Name:', s['name'][:70])
    
print('\n=== Cheapest Followers ===')
for s in insta_foll[:3]:
    print('ID:', s['service'], '| Price: $', s['rate'], '| Min:', s['min'], '| Name:', s['name'][:70])
