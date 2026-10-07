import sys

with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Change GIFT_BAL to 0.0
content = content.replace("GIFT_BAL = 3.0", "GIFT_BAL = 0.0")

# Add user_get_by_username
new_func = '''
def user_get_by_username(username):
    username = username.replace("@", "").strip()
    try:
        r = requests.get(f"{SUPA_URL}/users?username=ilike.*{username}*", headers=HEADERS)
        data = r.json()
        if data:
            u = data[0]
            return {
                "id": u["id"], 
                "username": u.get("username", ""),
                "name": u.get("username", ""), 
                "nickname": "", 
                "balance": u.get("balance", 0.0)
            }
        return None
    except Exception as e:
        print(f"[DB] get_by_username error: {e}")
        return None
'''

if 'def user_get_by_username' not in content:
    content += new_func

with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("supabase_db.py patched successfully")
