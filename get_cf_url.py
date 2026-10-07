import subprocess
import re
import time

p = subprocess.Popen(["cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:8080"], stderr=subprocess.PIPE, text=True)

url = None
for line in p.stderr:
    print(line, end='')
    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
    if match:
        url = match.group(0)
        break

if url:
    print(f"\n\nSUCCESS! URL IS: {url}")
else:
    print("\n\nFAILED TO FIND URL")
