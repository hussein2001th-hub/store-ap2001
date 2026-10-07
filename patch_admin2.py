import sys, re

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'# /add uid amount.*?return True', re.DOTALL)
match = pattern.search(content)

if match:
    new_admin = '''# /add uid amount OR /add @username amount
    if text.startswith("/add") and len(parts) == 3:
        try:
            target_user = parts[1]
            amt = float(parts[2])
            
            tid = None
            if target_user.startswith("@") or not target_user.isdigit():
                found_u = user_get_by_username(target_user)
                if found_u:
                    tid = found_u["id"]
                else:
                    send_text(chat_id, f"❌ لم يتم العثور على المستخدم: {target_user}")
                    return True
            else:
                tid = int(target_user)
                
            nb = user_add_balance(tid, amt)
            send_text(chat_id,
                      f"✅ تم إضافة <b>${amt:.4f}</b> للمستخدم <code>{tid} ({target_user})</code>\\n"
                      f"الرصيد الجديد: <b>${nb:.4f}</b>")
            send_text(tid,
                      f"🎁 <b>تم شحن حسابك بـ ${amt:.4f} بنجاح!</b>\\n"
                      f"رصيدك الحالي: <code>${nb:.4f}</code>")
        except Exception as e:
            send_text(chat_id, f"❌ خطأ: {e}\\nالاستخدام: /add user_id amount أو /add @username amount")
        return True'''
    content = content[:match.start()] + new_admin + content[match.end():]
    with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Regex patch successful!")
else:
    print("Regex failed to match")
