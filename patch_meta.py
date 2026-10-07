import os

path = r'c:\Users\حسين\Desktop\app\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

meta_tags = """
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
"""
if 'must-revalidate' not in html:
    html = html.replace('<head>', '<head>' + meta_tags)

html = html.replace('?v=4.0', '?v=5.0')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Meta cache busters added')
