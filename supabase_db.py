import requests
import json
import os

SUPA_URL = "https://nncfwhqmpfnmazlgqqgs.supabase.co/rest/v1"
SUPA_KEY = "sb_secret_4krUVM5rXrS6P3MDLZZEYg_NKYC0B4J"

HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

GIFT_BAL = 0.0

def init_db():
    print("[DB] Supabase mode ready.")

def user_get(uid, username="", first_name=""):
    try:
        r = requests.get(f"{SUPA_URL}/users?id=eq.{uid}", headers=HEADERS)
        data = r.json()
        if data:
            u = data[0]
            # Try to fetch missing columns safely
            first_name = first_name or u.get("username", "")
            return {
                "id": u["id"], 
                "username": u.get("username", ""),
                "name": first_name, 
                "nickname": "", 
                "balance": u.get("balance", 0.0)
            }
        
        # New user
        payload = {
            "id": uid,
            "username": username or first_name,
            "balance": GIFT_BAL
        }
        res = requests.post(f"{SUPA_URL}/users", headers=HEADERS, json=payload)
        return {
            "id": uid, 
            "username": username, 
            "name": first_name,
            "nickname": "", 
            "balance": GIFT_BAL
        }
    except Exception as e:
        print(f"[DB] user_get error: {e}")
        return {"id": uid, "username": username, "name": first_name, "nickname": "", "balance": 0.0}

def user_add_balance(uid, delta):
    try:
        u = requests.get(f"{SUPA_URL}/users?id=eq.{uid}&select=balance", headers=HEADERS).json()
        if not u: return 0.0
        new_bal = max(0, round(u[0].get("balance", 0.0) + delta, 4))
        payload = {"balance": new_bal}
        
        requests.patch(f"{SUPA_URL}/users?id=eq.{uid}", headers=HEADERS, json=payload)
        return new_bal
    except Exception as e:
        print(f"[DB] add_balance error: {e}")
        return 0.0

def user_set_balance(uid, amount):
    try:
        new_bal = round(float(amount), 4)
        payload = {"balance": new_bal}
        requests.patch(f"{SUPA_URL}/users?id=eq.{uid}", headers=HEADERS, json=payload)
        return new_bal
    except Exception as e:
        print(f"[DB] set_balance error: {e}")
        return round(float(amount), 4)

def user_set_nickname(uid, nick):
    pass # Supabase users table doesn't have nickname yet, ignoring for now

def users_list():
    try:
        r = requests.get(f"{SUPA_URL}/users?order=balance.desc&limit=50", headers=HEADERS)
        users = r.json()
        # Mocking sqlite Row object behavior: user_id, username, first_name, balance
        return [[u["id"], u.get("username", ""), "", u.get("balance", 0.0)] for u in users]
    except Exception as e:
        print(f"[DB] users_list error: {e}")
        return []

def users_all_ids():
    try:
        r = requests.get(f"{SUPA_URL}/users?select=id", headers=HEADERS)
        return [u["id"] for u in r.json()]
    except Exception as e:
        print(f"[DB] all_ids error: {e}")
        return []

def order_save(oid, uid, service, target, qty, cost):
    try:
        payload = {
            "id": oid,
            "user_id": uid,
            "service_name": service,
            "target": target,
            "quantity": qty,
            "cost": cost,
            "status": "pending"
        }
        requests.post(f"{SUPA_URL}/orders", headers=HEADERS, json=payload)
    except Exception as e:
        print(f"[DB] order_save error: {e}")

def order_update_status(oid, status):
    try:
        payload = {"status": status}
        r = requests.patch(f"{SUPA_URL}/orders?id=eq.{oid}", headers=HEADERS, json=payload)
        data = r.json()
        if data:
            return {"user_id": data[0]["user_id"], "service": data[0]["service_name"], "cost": data[0]["cost"]}
        return None
    except Exception as e:
        print(f"[DB] order_update error: {e}")
        return None

def user_orders(uid):
    try:
        r = requests.get(f"{SUPA_URL}/orders?user_id=eq.{uid}&order=id.desc&limit=20", headers=HEADERS)
        orders = r.json()
        return [{"id": o["id"], "service": o["service_name"], "target": o["target"], "qty": o["quantity"],
                 "cost": o["cost"], "status": "جاري التنفيذ" if o.get("status", "").startswith("api_id:") else o.get("status", "pending"), "date": o.get("created_at", "")} for o in orders]
    except Exception as e:
        print(f"[DB] user_orders error: {e}")
        return []

def recharge_save(uid, method, code, amount=0):
    try:
        payload = {
            "user_id": uid,
            "method": method,
            "code": code,
            "amount": amount,
            "status": "pending"
        }
        r = requests.post(f"{SUPA_URL}/recharges", headers=HEADERS, json=payload)
        data = r.json()
        return data[0]["id"] if data else 0
    except Exception as e:
        print(f"[DB] recharge_save error: {e}")
        return 0

def recharge_get(rid):
    try:
        r = requests.get(f"{SUPA_URL}/recharges?id=eq.{rid}", headers=HEADERS)
        data = r.json()
        if data:
            c = data[0]
            return {"id": c["id"], "user_id": c["user_id"], "method": c.get("method", ""),
                    "code": c.get("code", ""), "amount": c.get("amount", 0.0), "status": c.get("status", "pending")}
        return None
    except Exception as e:
        print(f"[DB] recharge_get error: {e}")
        return None

def recharge_update(rid, status):
    try:
        payload = {"status": status}
        requests.patch(f"{SUPA_URL}/recharges?id=eq.{rid}", headers=HEADERS, json=payload)
    except Exception as e:
        print(f"[DB] recharge_update error: {e}")

def order_get_tracked():
    try:
        r = requests.get(f"{SUPA_URL}/orders?status=like.api_id:*", headers=HEADERS)
        return r.json()
    except Exception as e:
        print(f"[DB] order_get_tracked error: {e}")
        return []

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
