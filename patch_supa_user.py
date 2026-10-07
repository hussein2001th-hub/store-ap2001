import sys

with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_funcs = '''
def user_check_username_exists(username):
    username = username.replace("@", "").strip()
    try:
        r = requests.get(f"{SUPA_URL}/users?username=ilike.{username}", headers=HEADERS)
        data = r.json()
        return len(data) > 0
    except Exception as e:
        print(f"[DB] check_username error: {e}")
        return True # fail safe, pretend it exists to prevent overwrite

def user_set_username(uid, username):
    username = username.replace("@", "").strip()
    try:
        payload = {"username": username}
        requests.patch(f"{SUPA_URL}/users?id=eq.{uid}", headers=HEADERS, json=payload)
    except Exception as e:
        print(f"[DB] set_username error: {e}")
'''

if 'def user_set_username' not in content:
    content += new_funcs
    with open(r'c:\Users\حسين\Desktop\app\supabase_db.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("supabase_db.py patched")
else:
    print("Already in supabase_db.py")
