import sys

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Keyboard
content = content.replace(
    '[{"text": "💬 الدعم الفني"}, {"text": "✏️ تغيير الاسم"}],',
    '[{"text": "💬 الدعم الفني"}, {"text": "✏️ إعداد يوزر الشحن"}],'
)

# 2. Update condition
content = content.replace(
    'if text in ("✏️ تغيير الاسم", "✏️ تغيير اسم المستخدم"):',
    'if text in ("✏️ تغيير الاسم", "✏️ تغيير اسم المستخدم", "✏️ إعداد يوزر الشحن"):'
)

# 3. Update cmd_change_name
old_cmd = '''def cmd_change_name(chat_id, uid):
    state_set(uid, "w_nick")
    send_text(chat_id,
              "✏️ <b>تغيير اسمك في المتجر</b>\\n\\nارسل الاسم الجديد:",
              kb_cancel())'''

new_cmd = '''def cmd_change_name(chat_id, uid):
    state_set(uid, "w_nick")
    send_text(chat_id,
              "✏️ <b>إعداد يوزر الشحن الخاص بك</b>\\n\\nهذا اليوزر سيستخدمه الإدارة لشحن رصيدك.\\nيجب أن يكون باللغة الإنجليزية وبدون مسافات (مثال: Ali_99).\\n\\nارسل اليوزر الجديد الآن:",
              kb_cancel())'''

if old_cmd in content:
    content = content.replace(old_cmd, new_cmd)

# 4. Update the await state handling
old_await = '''    # ── Change nickname ───────────────────────────────────────────────────────
    if s == "w_nick":
        nick = text.strip()[:50]
        if not nick:
            send_text(chat_id, "الاسم لا يمكن ان يكون فارغاً:", kb_cancel())
            return
        user_set_nickname(uid, nick)
        state_clear(uid)
        send_text(chat_id, f"✅ <b>تم تغيير اسمك الى: {nick}</b>")
        return'''

new_await = '''    # ── Change username ───────────────────────────────────────────────────────
    if s == "w_nick":
        nick = text.strip().replace("@", "")[:30]
        import re
        if not re.match("^[A-Za-z0-9_]{3,30}$", nick):
            send_text(chat_id, "❌ اليوزر غير صالح! يجب أن يحتوي على أحرف إنجليزية وأرقام فقط (بدون مسافات، من 3 إلى 30 حرف):", kb_cancel())
            return
        
        # Check if exists
        if user_check_username_exists(nick):
            send_text(chat_id, "❌ هذا اليوزر محجوز مسبقاً لشخص آخر! يرجى إرسال يوزر مختلف:", kb_cancel())
            return

        user_set_username(uid, nick)
        state_clear(uid)
        send_text(chat_id, f"✅ <b>تم حفظ يوزر الشحن بنجاح!</b>\\nاليوزر الخاص بك الآن هو: <code>@{nick}</code>\\nأرسل هذا اليوزر للإدارة عند طلب شحن رصيدك.")
        return'''

if old_await in content:
    content = content.replace(old_await, new_await)

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("bot_backend patched")
