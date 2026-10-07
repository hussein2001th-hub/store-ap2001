import os, sys, json, time, sqlite3, threading, urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests

# ── force UTF-8 on Windows ───────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN   = "8880725280:AAHsPD9XnAJw3Y_EZWvy3C6ivZNHI1jQrFA"
ADMIN_ID    = 1214772876          # @H99lh
ADMIN_PHONE = "07739439110"       # رقم حسين للتحويل عبر أسياسيل / زين كاش
WEBAPP_URL  = "https://hussein2001th-hub.github.io/-/"
SERVER_PORT = 8080
DB_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store_database.db")
API_URL     = f"https://api.telegram.org/bot{BOT_TOKEN}"
SUPPORT     = "@h99lh"
CHANNEL     = "https://t.me/h98lh"
GIFT_BAL    = 3.0

# SMM API Settings (JAP - Just Another Panel)
SMM_API_KEY = "606f5453864ee4341d5a41f297294350"
SMM_API_URL = "https://justanotherpanel.com/api/v2"

# مبالغ الشحن المتاحة بالدولار
RECHARGE_AMOUNTS = [1, 2, 3, 5, 7, 10]


# ============================================================
# DATABASE (Supabase)
# ============================================================
from supabase_db import *

# ============================================================
# STATE MACHINE (in-memory)
# ============================================================
_states = {}
_lock   = threading.Lock()

def state_get(uid):
    with _lock:
        return dict(_states.get(uid, {}))

def state_set(uid, s, data=None):
    with _lock:
        _states[uid] = {"s": s, "d": data or {}}

def state_clear(uid):
    with _lock:
        _states.pop(uid, None)

# ============================================================
# TELEGRAM API
# ============================================================

_session = requests.Session()

def tg_call(method, payload=None, timeout_sec=15):
    """Call Telegram Bot API. Returns (ok, result)."""
    try:
        r = _session.post(f"{API_URL}/{method}", json=payload, timeout=timeout_sec)
        data = r.json()
        if not data.get("ok"):
            desc = data.get("description", "unknown error")
            print(f"[TG] {method} failed: {desc}")
        return data
    except Exception as e:
        print(f"[TG] {method} exception: {e}")
        return {"ok": False}


def send_text(chat_id, text, reply_markup=None, parse_mode="HTML"):
    """Send a text message."""
    p = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        p["reply_markup"] = reply_markup
    return tg_call("sendMessage", p)


def edit_text(chat_id, message_id, text, reply_markup=None):
    """Edit an existing message."""
    p = {"chat_id": chat_id, "message_id": message_id,
         "text": text, "parse_mode": "HTML"}
    if reply_markup:
        p["reply_markup"] = reply_markup
    return tg_call("editMessageText", p)


def answer_cb(callback_id, text="", show_alert=False):
    """Answer a callback query."""
    tg_call("answerCallbackQuery",
            {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})


def notify_admin(text, reply_markup=None):
    """Send notification to admin."""
    if ADMIN_ID:
        send_text(ADMIN_ID, text, reply_markup)


# ============================================================
# KEYBOARDS
# ============================================================

def kb_main():
    """
    Main ReplyKeyboard — NO web_app button (HTTP localhost doesn't support it).
    The app link is sent separately as an inline button.
    """
    return {
        "keyboard": [
            [{"text": "📱 فتح التطبيق"}, {"text": "💲 شحن رصيدي"}],
            [{"text": "🎁 دعوة صديق"},  {"text": "📖 طريقة الاستخدام"}],
            [{"text": "💬 الدعم الفني"}, {"text": "✏️ إعداد يوزر الشحن"}],
            [{"text": "📋 تسجيل خروج"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }


def kb_open_app(uid, bal):
    """Inline keyboard with URL button to open the web store."""
    url = f"{WEBAPP_URL}?user_id={uid}&balance={bal:.4f}"
    return {
        "inline_keyboard": [[
            {"text": "📱 فتح متجر حسين أثير", "url": url}
        ]]
    }


def kb_charge():
    return {
        "inline_keyboard": [
            [{"text": "⭐ نجوم تيليكرام",       "callback_data": "ch:stars"}],
            [{"text": "📱 أسياسيل",             "callback_data": "ch:asia"}],
            [{"text": "💳 زين كاش",              "callback_data": "ch:zain"}],
            [{"text": "💳 ماستر الرافدين",       "callback_data": "ch:master"}],
            [{"text": "↩️ رجوع",                 "callback_data": "back"}]
        ]
    }


def kb_cancel():
    return {"inline_keyboard": [[{"text": "❌ إلغاء", "callback_data": "back"}]]}


def kb_logout():
    return {"inline_keyboard": [[
        {"text": "✅ نعم، خروج",  "callback_data": "logout_yes"},
        {"text": "❌ لا",         "callback_data": "back"}
    ]]}


def kb_admin_recharge(rid, uid, amount):
    return {"inline_keyboard": [[
        {"text": f"✅ قبول وشحن ${amount}",   "callback_data": f"aok:{rid}:{uid}:{amount}"},
        {"text": "❌ رفض",                    "callback_data": f"arej:{rid}:{uid}"}
    ]]}



def kb_recharge_amounts(method_key):
    """Inline keyboard: amount buttons $1-$10 for a given method."""
    rows = []
    row  = []
    for amt in RECHARGE_AMOUNTS:
        row.append({"text": f"${amt}", "callback_data": f"amt:{method_key}:{amt}"})
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([{"text": "↩️ رجوع", "callback_data": "back"}])
    return {"inline_keyboard": rows}


# ── Charge method definitions ─────────────────────────────────────────────────
#
#  Flow for asia / zain / master:
#    1. User taps method → sees amount buttons
#    2. User picks amount → bot shows ADMIN_PHONE + asks for user phone number
#    3. User sends phone → bot asks for transfer receipt/code
#    4. User sends code → bot saves recharge + notifies admin
#
#  Flow for stars:
#    1. User taps method → bot asks for star count + account name directly
#
CHARGE_INFO = {
    "stars": {
        "label": "نجوم تيليكرام",
        "has_amounts": False,
        "state": "w_stars",
        "msg": (
            "⭐ <b>الشحن عبر نجوم تيليكرام</b>\n\n"
            "1. افتح بروفايل البوت @ttbbegbot\n"
            "2. اضغط <b>ارسال نجوم</b>\n"
            "3. ارسلي عدد النجوم + اسم حسابك\n\n"
            "<b>مثال:</b> <code>100 نجمة من @myaccount</code>"
        )
    },
    "asia": {
        "label": "أسياسيل",
        "has_amounts": True,
        "state": "w_asia_phone",
        "msg": None   # generated dynamically after amount selection
    },
    "zain": {
        "label": "زين كاش",
        "has_amounts": True,
        "state": "w_zain_phone",
        "msg": None
    },
    "master": {
        "label": "ماستر الرافدين",
        "has_amounts": True,
        "state": "w_master_phone",
        "msg": None
    }
}

# States that wait for a phone number (step 2)
PHONE_STATES = {
    "w_asia_phone":   ("asia",   "أسياسيل"),
    "w_zain_phone":   ("zain",   "زين كاش"),
    "w_master_phone": ("master", "ماستر الرافدين"),
}

# States that wait for a transfer code (step 3)
CODE_STATES = {
    "w_asia_code":   ("asia",   "أسياسيل"),
    "w_zain_code":   ("zain",   "زين كاش"),
    "w_master_code": ("master", "ماستر الرافدين"),
}

# Simple states (no amount selection)
CHARGE_STATES = {"w_stars": ("stars", "نجوم تيليكرام")}


def charge_phone_msg(label, amount):
    """Build the 'send to this number' instruction message."""
    return (
        f"📱 <b>شحن {label} — ${amount}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"حوّل <b>${amount}</b> الى هذا الرقم:\n\n"
        f"📞 <code>{ADMIN_PHONE}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"بعد التحويل، ارسلي <b>رقم هاتفك</b> بهذا الشكل:\n"
        f"<code>077xxxxxxxx</code>"
    )


def charge_code_msg(label, amount, phone):
    """Ask user for transfer receipt/code after sending their phone."""
    return (
        f"✅ <b>تم استلام رقم هاتفك:</b> <code>{phone}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"الان ارسلي <b>كود عملية التحويل</b>\n"
        f"(الكود الذي يصلك برسالة بعد التحويل)\n\n"
        f"<b>مثال:</b> <code>TXN1234567</code>"
    )



# ============================================================
# MESSAGE HANDLERS
# ============================================================

def cmd_start(chat_id, uid, first_name, u):
    """Handle /start — sends welcome message + main keyboard."""
    state_clear(uid)
    bal  = u["balance"]
    nick = u.get("nickname") or first_name

    # Step 1: Send the main text + ReplyKeyboard (NO web_app button)
    send_text(
        chat_id,
        f"<b>اهلاً {nick} في متجر حسين أثير!</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 <b>رصيدك:</b> <code>${bal:.4f}</code>\n"
        f"🆔 <b>معرفك (ID):</b> <code>{uid}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📖 <b>طريقة الشحن:</b>\n"
        f"1️⃣ افتح التطبيق وسجل دخولك (تلقائي)\n"
        f"2️⃣ انسخ <b>اسم المستخدم</b> الخاص بك من ملفك الشخصي في التطبيق (مثال: h3g...)\n"
        f"3️⃣ اضغط على (شحن رصيدي) أدناه وأرسل اسم المستخدم مع التحويل لضمان وصول الرصيد بسرعة.\n\n"
        f"اختر من القائمة ادناه:",
        kb_main()
    )

    # Step 2: Send a separate inline button to open the web store
    send_text(
        chat_id,
        "اضغط الزر ادناه لفتح المتجر:",
        kb_open_app(uid, bal)
    )


def cmd_open_app(chat_id, uid, u):
    """Handle '📱 فتح التطبيق' button."""
    bal = u["balance"]
    send_text(
        chat_id,
        "اضغط الزر ادناه لفتح متجر حسين أثير:",
        kb_open_app(uid, bal)
    )


def cmd_charge(chat_id):
    send_text(chat_id, "💲 <b>شحن رصيدك</b>\n\nاختر طريقة الدفع:", kb_charge())


def cmd_balance(chat_id, uid):
    u      = user_get(uid)
    orders = user_orders(uid)
    spent  = sum(o["cost"] for o in orders)
    send_text(
        chat_id,
        f"💰 <b>محفظتك في متجر حسين أثير</b>\n\n"
        f"💵 الرصيد المتاح: <code>${u['balance']:.4f}</code>\n"
        f"📊 إجمالي المنفق: <code>${spent:.4f}</code>\n"
        f"🛒 عدد الطلبات: <code>{len(orders)}</code>"
    )


def cmd_invite(chat_id, uid):
    link = f"https://t.me/ttbbegbot?start=ref_{uid}"
    send_text(
        chat_id,
        f"🎁 <b>دعوة صديق وأكسب رصيد!</b>\n\n"
        f"رابط دعوتك:\n<code>{link}</code>\n\n"
        f"تحصل على <b>$0.50</b> لكل صديق ينضم!\n\n"
        f"قناتنا: {CHANNEL}"
    )


def cmd_howto(chat_id):
    send_text(
        chat_id,
        "📖 <b>طريقة الاستخدام</b>\n\n"
        "1️⃣ اضغط <b>📱 فتح التطبيق</b>\n"
        "2️⃣ اختر المنصة (إنستقرام، تيك توك...)\n"
        "3️⃣ اختر الخدمة والكمية المطلوبة\n"
        "4️⃣ أدخل رابط حسابك أو المنشور\n"
        "5️⃣ أكد الطلب وسيُنفذ فوراً\n\n"
        f"للاستفسار: {SUPPORT}"
    )


def cmd_support(chat_id):
    send_text(
        chat_id,
        f"💬 <b>الدعم الفني - متجر حسين أثير</b>\n\n"
        f"تواصل مع الدعم:\n👉 {SUPPORT}\n\n"
        f"قناة المتجر:\n👉 {CHANNEL}\n\n"
        f"متاح يومياً 9 صباحاً - 12 منتصف الليل"
    )


def cmd_change_name(chat_id, uid):
    state_set(uid, "w_nick")
    send_text(chat_id,
              "✏️ <b>إعداد يوزر الشحن الخاص بك</b>\n\nهذا اليوزر سيستخدمه الإدارة لشحن رصيدك.\nيجب أن يكون باللغة الإنجليزية وبدون مسافات (مثال: Ali_99).\n\nارسل اليوزر الجديد الآن:",
              kb_cancel())


def cmd_logout(chat_id):
    send_text(chat_id,
              "📋 <b>تسجيل الخروج</b>\n\nهل أنت متأكد؟ رصيدك لن يتأثر.",
              kb_logout())


# ── Admin commands ────────────────────────────────────────────────────────────

def handle_admin(chat_id, uid, text):
    """
    Handle admin-only commands.
    Returns True if the command was handled, False otherwise.
    """
    if uid != ADMIN_ID:
        return False

    parts = text.split()

    # /add uid amount OR /add @username amount
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
                      f"✅ تم إضافة <b>${amt:.4f}</b> للمستخدم <code>{tid} ({target_user})</code>\n"
                      f"الرصيد الجديد: <b>${nb:.4f}</b>")
            send_text(tid,
                      f"🎁 <b>تم شحن حسابك بـ ${amt:.4f} بنجاح!</b>\n"
                      f"رصيدك الحالي: <code>${nb:.4f}</code>")
        except Exception as e:
            send_text(chat_id, f"❌ خطأ: {e}\nالاستخدام: /add user_id amount أو /add @username amount")
        return True

    # /set uid amount
    if text.startswith("/set") and len(parts) == 3:
        try:
            tid, amt = int(parts[1]), float(parts[2])
            user_set_balance(tid, amt)
            send_text(chat_id, f"✅ رصيد {tid} اصبح ${amt:.4f}")
            send_text(tid, f"تم تحديث رصيدك الى: ${amt:.4f}")
        except Exception as e:
            send_text(chat_id, f"خطأ: {e}")
        return True

    # /dec uid amount
    if text.startswith("/dec") and len(parts) == 3:
        try:
            tid, amt = int(parts[1]), float(parts[2])
            nb = user_add_balance(tid, -amt)
            send_text(chat_id, f"✅ تم خصم ${amt:.4f} من {tid}\nرصيده: ${nb:.4f}")
        except Exception as e:
            send_text(chat_id, f"خطأ: {e}")
        return True

    # /users
    if text == "/users":
        rows  = users_list()
        lines = ["📋 <b>قائمة المشتركين:</b>\n"]
        for r in rows:
            uid_r = r[0] if isinstance(r, (list, tuple)) else r["user_id"]
            uname = r[1] if isinstance(r, (list, tuple)) else r["username"]
            fname = r[2] if isinstance(r, (list, tuple)) else r["first_name"]
            bal   = r[3] if isinstance(r, (list, tuple)) else r["balance"]
            lines.append(f"• <code>{uid_r}</code> @{uname or '-'} ({fname or '?'}): ${bal:.4f}")
        send_text(chat_id, "\n".join(lines))
        return True

    # /approve rid amount
    if text.startswith("/approve") and len(parts) == 3:
        try:
            rid, amt = int(parts[1]), float(parts[2])
            rec = recharge_get(rid)
            if not rec:
                send_text(chat_id, f"طلب #{rid} غير موجود")
                return True
            nb = user_add_balance(rec["user_id"], amt)
            recharge_update(rid, "مقبول")
            send_text(chat_id, f"✅ تم قبول #{rid} وشحن ${amt:.4f}")
            send_text(rec["user_id"],
                      f"🎉 <b>تم قبول طلب شحنك!</b>\n"
                      f"رقم الطلب: #{rid}\n"
                      f"المبلغ المضاف: ${amt:.4f}\n"
                      f"رصيدك الان: ${nb:.4f}")
        except Exception as e:
            send_text(chat_id, f"خطأ: {e}\nالصيغة: /approve rid amount")
        return True

    # /reject rid
    if text.startswith("/reject") and len(parts) == 2:
        try:
            rid = int(parts[1])
            rec = recharge_get(rid)
            if not rec:
                send_text(chat_id, f"طلب #{rid} غير موجود")
                return True
            recharge_update(rid, "مرفوض")
            send_text(chat_id, f"❌ تم رفض طلب #{rid}")
            send_text(rec["user_id"],
                      f"❌ تم رفض طلب شحنك #{rid}\nللاستفسار: {SUPPORT}")
        except Exception as e:
            send_text(chat_id, f"خطأ: {e}")
        return True

    # /update_order oid status [refund]
    if text.startswith("/update_order") and len(parts) >= 3:
        try:
            oid    = int(parts[1])
            status = parts[2]
            refund = float(parts[3]) if len(parts) >= 4 else 0.0
            order  = order_update_status(oid, status)
            if not order:
                send_text(chat_id, f"طلب #{oid} غير موجود")
                return True
            nb = order["cost"]
            if refund > 0:
                nb = user_add_balance(order["user_id"], refund)
            send_text(chat_id, f"✅ تم تحديث #{oid} الى: {status}")
            msg = f"تحديث الطلب #{oid}\nالحالة: {status}"
            if refund > 0:
                msg += f"\nتم ارجاع ${refund:.4f}\nرصيدك الان: ${nb:.4f}"
            send_text(order["user_id"], msg)
        except Exception as e:
            send_text(chat_id, f"خطأ: {e}")
        return True

    # /broadcast text
    if text.startswith("/broadcast "):
        msg_text = text[11:].strip()
        if msg_text:
            ids = users_all_ids()
            ok  = 0
            for tid in ids:
                try:
                    send_text(tid, f"📢 <b>اعلان من متجر حسين اثير:</b>\n\n{msg_text}")
                    ok += 1
                    time.sleep(0.05)
                except Exception:
                    pass
            send_text(chat_id, f"✅ تم الارسال لـ {ok}/{len(ids)} مستخدم")
        return True

    return False


# ── Awaiting state handlers ───────────────────────────────────────────────────

def handle_awaiting(chat_id, uid, text, st):
    s = st.get("s", "")
    d = st.get("d", {})

    # ── Change username ───────────────────────────────────────────────────────
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
        send_text(chat_id, f"✅ <b>تم حفظ يوزر الشحن بنجاح!</b>\nاليوزر الخاص بك الآن هو: <code>@{nick}</code>\nأرسل هذا اليوزر للإدارة عند طلب شحن رصيدك.")
        return

    # ── Stars: simple one-step ────────────────────────────────────────────────
    if s in CHARGE_STATES:
        method_key, method_label = CHARGE_STATES[s]
        code = text.strip()
        if len(code) < 3:
            send_text(chat_id, "ارسل المعلومات بشكل صحيح:", kb_cancel())
            return
        rid = recharge_save(uid, method_label, code)
        state_clear(uid)
        _send_charge_confirm(chat_id, uid, rid, method_label, "—", code, 0)
        return

    # ── Step 2: waiting for phone number ─────────────────────────────────────
    if s in PHONE_STATES:
        method_key, method_label = PHONE_STATES[s]
        phone = text.strip()
        # validate Iraqi phone (07xxxxxxxxx or 009647xxxxxxxxx)
        if not (7 <= len(phone) <= 15 and any(c.isdigit() for c in phone)):
            send_text(chat_id,
                      "رقم الهاتف غير صحيح.\nارسلي رقمك بهذا الشكل: <code>077xxxxxxxx</code>",
                      kb_cancel())
            return
        amount = d.get("amount", 0)
        # move to code-waiting state
        code_state = f"w_{method_key}_code"
        state_set(uid, code_state, {"method": method_key, "label": method_label,
                                     "phone": phone, "amount": amount})
        send_text(chat_id, charge_code_msg(method_label, amount, phone), kb_cancel())
        return

    # ── Step 3: waiting for transfer code ────────────────────────────────────
    if s in CODE_STATES:
        method_key, method_label = CODE_STATES[s]
        code   = text.strip()
        phone  = d.get("phone", "")
        amount = d.get("amount", 0)
        if len(code) < 3:
            send_text(chat_id, "ارسل الكود بشكل صحيح:", kb_cancel())
            return
        full_code = f"هاتف:{phone} | كود:{code}"
        rid = recharge_save(uid, method_label, full_code, amount)
        state_clear(uid)
        _send_charge_confirm(chat_id, uid, rid, method_label, phone, code, amount)
        return


def _send_charge_confirm(chat_id, uid, rid, method_label, phone, code, amount):
    """Send charge confirmation to user + notify admin."""
    amt_str = f"${amount}" if amount else "—"
    send_text(chat_id,
              f"✅ <b>تم استلام طلب شحنك!</b>\n\n"
              f"━━━━━━━━━━━━━━━━━━━━\n"
              f"🏦 الطريقة: <b>{method_label}</b>\n"
              f"💵 المبلغ: <b>{amt_str}</b>\n"
              f"📞 هاتفك: <code>{phone}</code>\n"
              f"🔑 الكود: <code>{code}</code>\n"
              f"🔢 رقم الطلب: <code>#{rid}</code>\n"
              f"━━━━━━━━━━━━━━━━━━━━\n\n"
              f"سيتم مراجعة طلبك وشحن رصيدك خلال دقائق.\n"
              f"للاستفسار: {SUPPORT}")

    u = user_get(uid)
    admin_kb = None
    if amount > 0:
        admin_kb = {
            "inline_keyboard": [[
                {"text": f"✅ قبول وشحن ${amount}",
                 "callback_data": f"aok:{rid}:{uid}:{amount}"},
                {"text": "❌ رفض",
                 "callback_data": f"arej:{rid}:{uid}"}
            ]]
        }
    notify_admin(
        f"💳 <b>طلب شحن جديد!</b>\n\n"
        f"رقم الطلب: <code>#{rid}</code>\n"
        f"المستخدم: <code>{uid}</code> @{u.get('username') or '-'}\n"
        f"الطريقة: <b>{method_label}</b>\n"
        f"المبلغ: <b>{amt_str}</b>\n"
        f"هاتفه: <code>{phone}</code>\n"
        f"الكود: <code>{code}</code>\n"
        f"رصيده: ${u['balance']:.4f}\n\n"
        f"<code>/approve {rid} {amount}</code>  |  <code>/reject {rid}</code>",
        admin_kb
    )


# ── Main message router ───────────────────────────────────────────────────────

def on_message(msg):
    try:
        chat_id = msg.get("chat", {}).get("id")
        fr      = msg.get("from", {})
        uid     = fr.get("id")
        uname   = fr.get("username", "")
        fname   = fr.get("first_name", "مستخدم")
        text    = (msg.get("text") or "").strip()

        # Ignore non-text messages except web_app_data
        if msg.get("web_app_data"):
            try:
                data = json.loads(msg["web_app_data"].get("data", "{}"))
                send_text(chat_id,
                          f"تم استلام بيانات:\n<code>{json.dumps(data, ensure_ascii=False)}</code>")
            except Exception:
                pass
            return

        if not text:
            return

        # Load user from DB
        u = user_get(uid, uname, fname)

        # 1. Admin commands
        if handle_admin(chat_id, uid, text):
            return

        # 2. Awaiting state (user is expected to type something)
        st = state_get(uid)
        if st:
            handle_awaiting(chat_id, uid, text, st)
            return

        # 3. Main menu commands
        if text.startswith("/start"):
            # Handle referral link
            parts = text.split()
            if len(parts) > 1 and parts[1].startswith("ref_"):
                try:
                    ref_uid = int(parts[1][4:])
                    if ref_uid != uid:
                        nb = user_add_balance(ref_uid, 0.5)
                        send_text(ref_uid,
                                  f"🎁 انضم صديق عبر رابطك!\n"
                                  f"تمت اضافة $0.50 لرصيدك.\n"
                                  f"رصيدك: ${nb:.4f}")
                except Exception:
                    pass
            cmd_start(chat_id, uid, fname, u)
            return

        if text == "📱 فتح التطبيق":
            cmd_open_app(chat_id, uid, u)
            return

        if text == "💲 شحن رصيدي":
            cmd_charge(chat_id)
            return

        if text in ("💰 رصيدي الحالي", "رصيدي"):
            cmd_balance(chat_id, uid)
            return

        if text == "🎁 دعوة صديق":
            cmd_invite(chat_id, uid)
            return

        if text == "📖 طريقة الاستخدام":
            cmd_howto(chat_id)
            return

        if text in ("💬 الدعم الفني", "📞 الدعم الفني"):
            cmd_support(chat_id)
            return

        if text in ("✏️ تغيير الاسم", "✏️ تغيير اسم المستخدم", "✏️ إعداد يوزر الشحن"):
            cmd_change_name(chat_id, uid)
            return

        if text == "📋 تسجيل خروج":
            cmd_logout(chat_id)
            return

        # Default reply
        send_text(chat_id, "لم افهم هذا الامر.\n\nارسل /start لعرض القائمة.")

    except Exception as e:
        print(f"[Bot] on_message error: {e}")


# ── Callback query handler ────────────────────────────────────────────────────

def on_callback(cb):
    try:
        chat_id    = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        fr         = cb.get("from", {})
        uid        = fr.get("id")
        uname      = fr.get("username", "")
        fname      = fr.get("first_name", "مستخدم")
        data       = cb.get("data", "")

        answer_cb(cb["id"])
        u = user_get(uid, uname, fname)

        # Back button
        if data == "back":
            state_clear(uid)
            edit_text(chat_id, message_id,
                      f"القائمة الرئيسية\nرصيدك: ${u['balance']:.4f}")
            return

        # Charge method selection
        if data.startswith("ch:"):
            key  = data[3:]
            info = CHARGE_INFO.get(key)
            if not info:
                return
            if info.get("has_amounts"):
                # Show amount selection keyboard
                edit_text(chat_id, message_id,
                          f"💲 <b>اختر المبلغ — {info['label']}</b>\n\n"
                          f"اضغط على المبلغ الذي تريد شحنه:",
                          kb_recharge_amounts(key))
            else:
                # Stars: go directly to code input
                state_set(uid, info["state"], {"method": key})
                edit_text(chat_id, message_id, info["msg"], kb_cancel())
            return

        # Amount selected → show transfer instructions + ask for phone
        if data.startswith("amt:"):
            _, key, amt_str = data.split(":")
            amount = float(amt_str)
            info   = CHARGE_INFO.get(key)
            if not info:
                return
            state_set(uid, info["state"], {"method": key, "amount": amount})
            edit_text(chat_id, message_id,
                      charge_phone_msg(info["label"], amount),
                      kb_cancel())
            return

        # Logout confirmation
        if data == "logout_yes":
            state_clear(uid)
            edit_text(chat_id, message_id,
                      "تم تسجيل خروجك.\nارسل /start للعودة في اي وقت.")
            return

        # Admin: approve recharge
        if data.startswith("aok:") and uid == ADMIN_ID:
            _, rid, tuid, amt = data.split(":")
            rid, tuid, amt = int(rid), int(tuid), float(amt)
            nb = user_add_balance(tuid, amt)
            recharge_update(rid, "مقبول")
            edit_text(chat_id, message_id,
                      f"✅ تم قبول #{rid} وشحن ${amt:.4f}\n"
                      f"رصيد المستخدم: ${nb:.4f}")
            send_text(tuid,
                      f"🎉 <b>تم قبول طلب شحنك!</b>\n"
                      f"رقم الطلب: #{rid}\n"
                      f"المبلغ: ${amt:.4f}\n"
                      f"رصيدك الان: ${nb:.4f}")
            return

        # Admin: reject recharge
        if data.startswith("arej:") and uid == ADMIN_ID:
            _, rid, tuid = data.split(":")
            rid, tuid = int(rid), int(tuid)
            recharge_update(rid, "مرفوض")
            edit_text(chat_id, message_id, f"❌ تم رفض طلب #{rid}")
            send_text(tuid,
                      f"❌ تم رفض طلب شحنك #{rid}\n"
                      f"للاستفسار: {SUPPORT}")
            return

    except Exception as e:
        print(f"[Bot] on_callback error: {e}")


# ============================================================
# LONG POLLING
# ============================================================
def polling_loop():
    print(f"[Bot] Polling started. Admin ID: {ADMIN_ID}")
    offset = 0
    while True:
        try:
            result = tg_call("getUpdates", {
                "offset": offset,
                "timeout": 30,
                "allowed_updates": ["message", "callback_query"]
            }, timeout_sec=40)
            
            if not result.get("ok"):
                time.sleep(1)
                continue

            for item in result.get("result", []):
                offset = item["update_id"] + 1
                if "message" in item:
                    import threading
                    threading.Thread(target=on_message, args=(item["message"],), daemon=True).start()
                elif "callback_query" in item:
                    import threading
                    threading.Thread(target=on_callback, args=(item["callback_query"],), daemon=True).start()

        except requests.exceptions.ConnectionError:
            print("[Bot] Connection lost. Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"[Bot] Polling error: {e}")
            time.sleep(3)


# ============================================================
# WEB SERVER + REST API
# ============================================================
class StoreHandler(SimpleHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # only log API calls
        if args and "/api/" in str(args[0]):
            print(f"[HTTP] {args[0]} {args[1] if len(args) > 1 else ''}")

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs     = urllib.parse.parse_qs(parsed.query)

        # /api/user?id=<uid>
        if parsed.path == "/api/user":
            try:
                uid = int(qs.get("id", [None])[0])
                u   = user_get(uid)
                self._send_json({
                    "success": True,
                    "user_id": uid,
                    "balance": u["balance"],
                    "orders":  user_orders(uid)
                })
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})
            return

        # Serve static files
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception:
            body = {}

        # /api/order
        if parsed.path == "/api/order":
            try:
                uid    = int(body.get("user_id", 0))
                svc    = body.get("service_name", "")
                target = body.get("target", "")
                qty    = int(body.get("qty", 0))
                cost   = float(body.get("cost", 0))
                oid    = int(body.get("order_id", int(time.time())))
                u      = user_get(uid)

                if u["balance"] < cost:
                    self._send_json({"success": False, "message": "رصيدك غير كافٍ"})
                    return

                # Try to extract service_id from frontend name like "[123] Followers"
                smm_service_id = None
                if svc.startswith("[") and "]" in svc:
                    try:
                        smm_service_id = int(svc.split("]")[0][1:])
                    except ValueError:
                        pass
                
                # Default status is 'pending'
                order_status = "قيد الانتظار"
                smm_response_msg = ""
                api_success = False
                
                if smm_service_id:
                    try:
                        payload = {
                            "key": SMM_API_KEY,
                            "action": "add",
                            "service": smm_service_id,
                            "link": target,
                            "quantity": qty
                        }
                        r = requests.post(SMM_API_URL, data=payload, timeout=15)
                        smm_resp = r.json()
                        
                        if "order" in smm_resp:
                            order_status = f"api_id:{smm_resp['order']}"
                            smm_response_msg = f"\n✅ تم ارساله بنجاح لـ JAP (ID: {smm_resp['order']})"
                            api_success = True
                        elif "error" in smm_resp:
                            # ⚠️ إذا رد الـ API بخطأ لا نخصم الرصيد!
                            error_msg = smm_resp['error']
                            self._send_json({"success": False, "message": f"خطأ من المزود: {error_msg}"})
                            return
                    except Exception as e:
                        self._send_json({"success": False, "message": "فشل الاتصال بالمزود، يرجى المحاولة لاحقاً."})
                        return
                else:
                    api_success = True # Manual order, assume success to deduct balance

                # 💡 بمجرد استلام رقم الطلب (وهذا يعني أن المزود قبل الطلب)، نخصم التكلفة
                nb = user_add_balance(uid, -cost)

                # Save order to local DB
                order_save(oid, uid, svc, target, qty, cost)
                if order_status != "قيد الانتظار":
                    order_update_status(oid, order_status)

                notify_admin(
                    f"طلب رشق جديد! #{oid}\n"
                    f"الخدمة: {svc}\n"
                    f"الرابط: {target}\n"
                    f"الكمية: {qty} | التكلفة: ${cost:.4f}\n"
                    f"المستخدم: {uid} | رصيده: ${nb:.4f}"
                    f"{smm_response_msg}\n\n"
                    f"تحديث: /update_order {oid} [حالة] [استرداد]"
                )
                
                send_text(uid,
                          f"طلب جديد #{oid}\n"
                          f"تم إنشاء الطلب رقم {oid}، وتم خصم ${cost:.4f} من رصيدك.")

                self._send_json({"success": True, "balance": nb, "order_id": oid})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})
            return

        # /api/recharge
        if parsed.path == "/api/recharge":
            try:
                uid    = int(body.get("user_id", 0))
                method = body.get("method", "")
                code   = body.get("code", "")
                amount = float(body.get("amount", 0))
                u      = user_get(uid)
                rid    = recharge_save(uid, method, code, amount)

                notify_admin(
                    f"طلب شحن من المتجر! #{rid}\n"
                    f"الطريقة: {method}\n"
                    f"الكود: {code}\n"
                    f"المستخدم: {uid} @{u.get('username') or '-'}\n"
                    f"المبلغ: ${amount:.4f}\n\n"
                    f"/approve {rid} {amount}\n/reject {rid}"
                )
                self._send_json({"success": True, "ref_id": rid})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})
            return

        # /api/update_order
        if parsed.path == "/api/update_order":
            try:
                oid    = int(body.get("order_id", 0))
                status = body.get("status", "")
                refund = float(body.get("refund", 0))
                order  = order_update_status(oid, status)
                if not order:
                    self._send_json({"success": False, "error": "Order not found"})
                    return
                nb = order["cost"]
                if refund > 0:
                    nb = user_add_balance(order["user_id"], refund)
                msg = f"تحديث الطلب #{oid}\nالحالة: {status}"
                if refund > 0:
                    msg += f"\nتم ارجاع ${refund:.4f}\nرصيدك الان: ${nb:.4f}"
                send_text(order["user_id"], msg)
                self._send_json({"success": True, "balance": nb})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})
            return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)



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
                                f"تهانينا طلبك أكتمل بنجاح\n"
                                f"رقم الطلب : {o['id']}\n"
                                f"حالة الطلب : مكتمل\n"
                                f"الرابط: {o.get('target', 'بدون رابط')}"
                            )
                        elif smm_status.lower() in ["canceled", "cancelled"]:
                            order_update_status(o["id"], "ملغى")
                            # Refund user
                            nb = user_add_balance(o["user_id"], float(o["cost"]))
                            send_text(
                                o["user_id"],
                                f"❌ تم إلغاء طلبك رقم {o['id']}\n"
                                f"تم استرجاع المبلغ: ${o['cost']} إلى رصيدك.\n"
                                f"الرصيد الحالي: ${nb:.4f}"
                            )
                        elif smm_status.lower() == "partial":
                            order_update_status(o["id"], "مكتمل جزئياً")
                            # Could do partial refund here if we calculate it
        except Exception as e:
            print(f"[Tracker Error] {e}")


def run_web_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(("0.0.0.0", SERVER_PORT), StoreHandler)
    print(f"[Web] Running on http://localhost:{SERVER_PORT}")
    server.serve_forever()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print(" Hussein Atheer Store - Bot & Web Server")
    print(f" Admin ID: {ADMIN_ID}")
    print("=" * 55)

    init_db()

    # Start web server in background thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Verify bot token (retry on timeout)
    print("[Bot] Connecting to Telegram...")
    for attempt in range(10):
        info = tg_call("getMe")
        if info.get("ok"):
            bot = info["result"]
            print(f"[Bot] Connected as @{bot['username']} (ID: {bot['id']})")
            break
        else:
            print(f"[Bot] Connection attempt {attempt+1}/10 failed, retrying in 5s...")
            time.sleep(5)
    else:
        print("[Bot] Could not connect to Telegram after 10 attempts.")
        print("[Bot] Web server is still running. Bot polling will start when connection restores.")

    # Start polling (runs forever in main thread)
    try:
        polling_loop()
    except KeyboardInterrupt:
        print("[Bot] Stopped by user.")
