import os
import re

path = r'c:\Users\حسين\Desktop\app\assets\js\services\storageService.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_state = """const INITIAL_STATE = {
        version: "2.7.0",
        balance: 0.0,
        orders: [],
        notifications: [],
        theme: "light"
    };"""

content = re.sub(r'const INITIAL_STATE = \{.*?\};', new_state, content, flags=re.DOTALL)

if 'localStorage.removeItem' not in content:
    content = content.replace('function init() {', 'function init() { localStorage.removeItem(STORAGE_KEY);')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("storageService updated!")
