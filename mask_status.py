import sys

with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_mask = '"status": o.get("status", "pending")'
new_mask = '"status": "جاري التنفيذ" if o.get("status", "").startswith("api_id:") else o.get("status", "pending")'

if old_mask in content:
    content = content.replace(old_mask, new_mask)
    with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Masked successfully")
else:
    print("Already masked or not found")
