import sys

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = '''                if u["balance"] < cost:
                    self._send_json({"success": False, "message": "رصيدك غير كافٍ"})
                    return

                # Deduct balance
                nb = user_add_balance(uid, -cost)

                # Try to extract service_id from frontend name like "[123] Followers"
                smm_service_id = None
                if svc.startswith("[") and "]" in svc:
                    try:
                        smm_service_id = int(svc.split("]")[0][1:])
                    except ValueError:
                        pass
                
                # Default status is 'pending', if sent successfully it will be updated
                order_status = "قيد الانتظار"
                smm_response_msg = ""
                
                if smm_service_id:
                    # Place order via API
                    try:
                        payload = {
                            "key": SMM_API_KEY,
                            "action": "add",
                            "service": smm_service_id,
                            "link": target,
                            "quantity": qty
                        }
                        r = requests.post(SMM_API_URL, data=payload, timeout=10)
                        smm_resp = r.json()
                        
                        if "order" in smm_resp:
                            order_status = "جاري التنفيذ"
                            smm_response_msg = f"\\n✅ تم ارساله بنجاح لـ JAP (ID: {smm_resp['order']})"
                        elif "error" in smm_resp:
                            smm_response_msg = f"\\n⚠️ خطأ من JAP: {smm_resp['error']}"
                    except Exception as e:
                        smm_response_msg = f"\\n⚠️ فشل الاتصال بالـ API: {e}"
                else:
                    smm_response_msg = "\\n⚠️ لم يتم العثور على Service ID، تم تسجيله كطلب يدوي."

                # Save order to local DB
                order_save(oid, uid, svc, target, qty, cost)
                if order_status != "قيد الانتظار":
                    order_update_status(oid, order_status)

                notify_admin(
                    f"طلب رشق جديد! #{oid}\\n"
                    f"الخدمة: {svc}\\n"
                    f"الرابط: {target}\\n"
                    f"الكمية: {qty} | التكلفة: ${cost:.4f}\\n"
                    f"المستخدم: {uid} | رصيده: ${nb:.4f}"
                    f"{smm_response_msg}\\n\\n"
                    f"تحديث: /update_order {oid} [حالة] [استرداد]"
                )
                
                send_text(uid,
                          f"✅ تم استلام طلبك وبدأ التنفيذ!\\n"
                          f"#{oid} | {svc}\\n"
                          f"التكلفة: ${cost:.4f} | رصيدك: ${nb:.4f}")

                self._send_json({"success": True, "balance": nb, "order_id": oid})'''

new_logic = '''                if u["balance"] < cost:
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
                            order_status = "جاري التنفيذ"
                            smm_response_msg = f"\\n✅ تم ارساله بنجاح لـ JAP (ID: {smm_resp['order']})"
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
                    f"طلب رشق جديد! #{oid}\\n"
                    f"الخدمة: {svc}\\n"
                    f"الرابط: {target}\\n"
                    f"الكمية: {qty} | التكلفة: ${cost:.4f}\\n"
                    f"المستخدم: {uid} | رصيده: ${nb:.4f}"
                    f"{smm_response_msg}\\n\\n"
                    f"تحديث: /update_order {oid} [حالة] [استرداد]"
                )
                
                send_text(uid,
                          f"✅ تم استلام طلبك بنجاح!\\n"
                          f"#{oid} | {svc}\\n"
                          f"التكلفة: ${cost:.4f} | رصيدك المتبقي: ${nb:.4f}")

                self._send_json({"success": True, "balance": nb, "order_id": oid})'''

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH SUCCESSFUL")
else:
    print("COULD NOT FIND OLD LOGIC BLOCK")
