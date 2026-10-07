import sys

with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''
def order_get_tracked():
    try:
        r = requests.get(f"{SUPA_URL}/orders?status=like.api_id:*", headers=HEADERS)
        return r.json()
    except Exception as e:
        print(f"[DB] order_get_tracked error: {e}")
        return []
'''

if 'def order_get_tracked():' not in content:
    content += new_func
    with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'w', encoding='utf-8') as f:
        f.write(content)
print("Updated supabase_db.py")
