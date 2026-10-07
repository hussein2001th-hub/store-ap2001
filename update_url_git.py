import os

path = r'c:\Users\حسين\Desktop\app\bot_backend.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

import re
content = re.sub(r'WEBAPP_URL\s*=\s*".*?"', 'WEBAPP_URL  = "https://hussein2001th-hub.github.io/-/"', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated WEBAPP_URL to GitHub Pages")
