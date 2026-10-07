import sys
import re

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

force_sub_code = '''
# ============================================================
# FORCE SUBSCRIPTION
# ============================================================
FORCE_SUB_CHANNEL = "@h98lh"

def check_subscription(uid):
    if uid == ADMIN_ID:
        return True
    try:
        r = tg_call("getChatMember", {"chat_id": FORCE_SUB_CHANNEL, "user_id": uid}, timeout_sec=5)
        if r.get("ok"):
            status = r.get("result", {}).get("status", "")
            if status in ["member", "administrator", "creator"]:
                return True
    except:
        pass
    return False

def send_force_sub_message(chat_id):
    markup = {
        "inline_keyboard": [
            [{"text": "📢 اضغط هنا للاشتراك", "url": f"https://t.me/{FORCE_SUB_CHANNEL[1:]}"}],
            [{"text": "✅ تحقق من الاشتراك", "callback_data": "check_sub"}]
        ]
    }
    send_text(chat_id, 
              "⚠️ <b>عذراً، يجب عليك الاشتراك في قناة المتجر أولاً.</b>\\n\\n"
              "يرجى الانضمام إلى القناة الرسمية للحصول على آخر التحديثات والخدمات، ثم اضغط على زر التحقق للمتابعة.", 
              reply_markup=json.dumps(markup))
'''

if "def check_subscription" not in content:
    content = content.replace("# ============================================================\n# TELEGRAM HANDLERS", force_sub_code + "\n# ============================================================\n# TELEGRAM HANDLERS")


# Patch on_message
msg_start = '''def on_message(msg):
    try:
        chat_id = msg["chat"]["id"]
        uid = msg["from"]["id"]'''

msg_sub_check = '''def on_message(msg):
    try:
        chat_id = msg["chat"]["id"]
        uid = msg["from"]["id"]
        
        if not check_subscription(uid):
            send_force_sub_message(chat_id)
            return
'''
content = content.replace(msg_start, msg_sub_check)


# Patch on_callback
cb_start = '''def on_callback(cb):
    try:
        cb_id = cb["id"]
        uid = cb["from"]["id"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data", "")
        msg_id = cb["message"]["message_id"]'''

cb_sub_check = '''def on_callback(cb):
    try:
        cb_id = cb["id"]
        uid = cb["from"]["id"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data", "")
        msg_id = cb["message"]["message_id"]

        if data == "check_sub":
            if check_subscription(uid):
                answer_cb(cb_id, "✅ تم التحقق، شكراً لاشتراكك!", show_alert=True)
                # re-trigger start
                u = user_get(uid)
                cmd_start(chat_id, uid, cb["from"].get("first_name", ""), u)
            else:
                answer_cb(cb_id, "❌ لم تقم بالاشتراك في القناة بعد!", show_alert=True)
            return

        if not check_subscription(uid):
            answer_cb(cb_id, "يجب الاشتراك في القناة أولاً!", show_alert=True)
            send_force_sub_message(chat_id)
            return
'''
content = content.replace(cb_start, cb_sub_check)

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("FORCE SUB PATCH APPLIED")
