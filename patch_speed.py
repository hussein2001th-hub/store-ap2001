import sys

with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_loop = """            for item in result.get("result", []):
                offset = item["update_id"] + 1
                if "message" in item:
                    on_message(item["message"])
                elif "callback_query" in item:
                    on_callback(item["callback_query"])"""

new_loop = """            for item in result.get("result", []):
                offset = item["update_id"] + 1
                if "message" in item:
                    import threading
                    threading.Thread(target=on_message, args=(item["message"],), daemon=True).start()
                elif "callback_query" in item:
                    import threading
                    threading.Thread(target=on_callback, args=(item["callback_query"],), daemon=True).start()"""

if old_loop in content:
    content = content.replace(old_loop, new_loop)
    with open(r'c:\Users\حسين\Desktop\app\bot_backend.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH APPLIED")
else:
    print("NOT FOUND")
