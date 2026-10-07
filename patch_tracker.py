import sys
import re

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the send_text for user when order placed
old_send_text = '''                send_text(uid,
                          f"✅ تم استلام طلبك بنجاح!\\n"
                          f"#{oid} | {svc}\\n"
                          f"التكلفة: ${cost:.4f} | رصيدك المتبقي: ${nb:.4f}")'''

new_send_text = '''                send_text(uid,
                          f"طلب جديد #{oid}\\n"
                          f"تم إنشاء الطلب رقم {oid}، وتم خصم ${cost:.4f} من رصيدك.")'''
content = content.replace(old_send_text, new_send_text)

# 2. Update the order_status to store the API ID
old_order_status = '''                        if "order" in smm_resp:
                            order_status = "جاري التنفيذ"'''

new_order_status = '''                        if "order" in smm_resp:
                            order_status = f"api_id:{smm_resp['order']}"'''
content = content.replace(old_order_status, new_order_status)

# 3. Add background thread for status checking
tracker_logic = '''
def order_tracker_loop():
    while True:
        try:
            import time
            time.sleep(60) # Check every 60 seconds
            
            # Get orders that are tracked
            tracked_orders = order_get_tracked()
            for o in tracked_orders:
                status_str = o.get("status", "")
                if status_str.startswith("api_id:"):
                    api_id = status_str.split(":")[1]
                    
                    # Query JAP API
                    payload = {
                        "key": SMM_API_KEY,
                        "action": "status",
                        "order": api_id
                    }
                    r = requests.post(SMM_API_URL, data=payload, timeout=10)
                    resp = r.json()
                    
                    if "status" in resp:
                        smm_status = resp["status"]
                        # Common statuses: Pending, In progress, Completed, Partial, Canceled, Processing
                        if smm_status.lower() == "completed":
                            # Update DB
                            order_update_status(o["id"], "مكتمل")
                            # Notify User
                            send_text(
                                o["user_id"],
                                f"تهانينا طلبك أكتمل بنجاح\\n"
                                f"رقم الطلب : {o['id']}\\n"
                                f"حالة الطلب : مكتمل\\n"
                                f"الرابط: {o.get('target', 'بدون رابط')}"
                            )
                        elif smm_status.lower() in ["canceled", "cancelled"]:
                            order_update_status(o["id"], "ملغى")
                            # Refund user
                            nb = user_add_balance(o["user_id"], float(o["cost"]))
                            send_text(
                                o["user_id"],
                                f"❌ تم إلغاء طلبك رقم {o['id']}\\n"
                                f"تم استرجاع المبلغ: ${o['cost']} إلى رصيدك.\\n"
                                f"الرصيد الحالي: ${nb:.4f}"
                            )
                        elif smm_status.lower() == "partial":
                            order_update_status(o["id"], "مكتمل جزئياً")
                            # Could do partial refund here if we calculate it
        except Exception as e:
            print(f"[Tracker Error] {e}")

'''

if "def order_tracker_loop():" not in content:
    content = content.replace("def run_web_server():", tracker_logic + "\ndef run_web_server():")

run_thread_logic = '''
    # Start telegram polling
    t1 = threading.Thread(target=polling_loop, daemon=True)
    t1.start()

    # Start order tracker
    t3 = threading.Thread(target=order_tracker_loop, daemon=True)
    t3.start()
'''
content = content.replace('''
    # Start telegram polling
    t1 = threading.Thread(target=polling_loop, daemon=True)
    t1.start()''', run_thread_logic)

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied to bot_backend.py")
