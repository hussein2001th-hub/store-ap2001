import os

path = r'c:\Users\حسين\Desktop\app\bot_backend.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('WEBAPP_URL  = "http://localhost:8080"', 'WEBAPP_URL  = "https://dd99a2ed62cd08.lhr.life"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated WEBAPP_URL to HTTPS tunnel")
