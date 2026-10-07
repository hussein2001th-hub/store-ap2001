import os

path = r'c:\Users\حسين\Desktop\app\bot_backend.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_headers = """    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()"""

new_headers = """    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()"""

if old_headers in content:
    content = content.replace(old_headers, new_headers)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Headers patched")
else:
    print("Headers block not found")
