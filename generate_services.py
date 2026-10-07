import json

path = r'C:\Users\حسين\.gemini\antigravity\brain\b6087634-64da-4015-b29d-97074e858c8c\.system_generated\steps\656\content.md'
try:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
except UnicodeDecodeError:
    with open(path, 'r', encoding='windows-1256') as f:
        text = f.read()

json_str = text.split('\n---\n\n')[1]
services = json.loads(json_str)

def find_best(keyword_cat, keyword_name, require_refill=False, max_price=5.0):
    candidates = []
    for s in services:
        cat = s.get('category', '').lower()
        name = s.get('name', '').lower()
        if keyword_cat in cat and keyword_name in name:
            if require_refill and ('refill' not in name and '30' not in name and '365' not in name and 'guarant' not in name):
                continue
            rate = float(s.get('rate', 9999))
            if rate <= max_price:
                candidates.append(s)
    candidates.sort(key=lambda x: float(x.get('rate', 9999)))
    return candidates[0] if candidates else None

res = {
    'insta_foll': find_best('instagram', 'follower', True),
    'insta_likes': find_best('instagram', 'like'),
    'insta_views': find_best('instagram', 'view'),
    'tiktok_foll': find_best('tiktok', 'follower', True),
    'tiktok_views': find_best('tiktok', 'view'),
    'tiktok_likes': find_best('tiktok', 'like'),
    'tele_members': find_best('telegram', 'member'),
    'tele_views': find_best('telegram', 'view')
}

out_script = f'''
window.StoreApp = window.StoreApp || {{}};
window.StoreApp.Config = window.StoreApp.Config || {{}};

window.StoreApp.Config.ServicesCatalog = [
    {{
        id: "instagram", name: "إنستغرام", desc: "متابعين • لايكات • مشاهدات",
        icon: "fab fa-instagram", iconClass: "icon-insta", category: "social", popular: true,
        services: [
            {{
                id: "insta-followers-30d", numId: {res['insta_foll']['service']},
                name: "[{res['insta_foll']['service']}] متابعين إنستغرام (مع ضمان)",
                rate: {res['insta_foll']['rate']}, min: {res['insta_foll']['min']}, max: {res['insta_foll']['max']},
                unit: 1000, badge: "🛡️ مع ضمان", speed: "⚡ سريع",
                label: "رابط الحساب أو اليوزر (@username)", placeholder: "https://instagram.com/username أو @username", type: "standard"
            }},
            {{
                id: "insta-likes", numId: {res['insta_likes']['service']},
                name: "[{res['insta_likes']['service']}] لايكات إنستغرام",
                rate: {res['insta_likes']['rate']}, min: {res['insta_likes']['min']}, max: {res['insta_likes']['max']},
                unit: 1000, badge: "⚡ فوري", speed: "🚀 فوري",
                label: "رابط المنشور (Post Link)", placeholder: "https://instagram.com/p/xxx", type: "standard"
            }},
            {{
                id: "insta-views", numId: {res['insta_views']['service']},
                name: "[{res['insta_views']['service']}] مشاهدات إنستغرام (ريلز/فيديو)",
                rate: {res['insta_views']['rate']}, min: {res['insta_views']['min']}, max: {res['insta_views']['max']},
                unit: 1000, badge: "🔥 حصري", speed: "⚡ سريع جداً",
                label: "رابط الريلز (Reel Link)", placeholder: "https://instagram.com/reel/xxx", type: "standard"
            }}
        ]
    }},
    {{
        id: "tiktok", name: "تيك توك", desc: "متابعين • لايكات • مشاهدات",
        icon: "fab fa-tiktok", iconClass: "icon-tiktok", category: "video", popular: true,
        services: [
            {{
                id: "tiktok-followers", numId: {res['tiktok_foll']['service']},
                name: "[{res['tiktok_foll']['service']}] متابعين تيك توك (مع ضمان)",
                rate: {res['tiktok_foll']['rate']}, min: {res['tiktok_foll']['min']}, max: {res['tiktok_foll']['max']},
                unit: 1000, badge: "⭐ ممتاز", speed: "⚡ سريع",
                label: "رابط الحساب أو اليوزر (@user)", placeholder: "https://tiktok.com/@username", type: "standard"
            }},
            {{
                id: "tiktok-likes", numId: {res['tiktok_likes']['service']},
                name: "[{res['tiktok_likes']['service']}] لايكات تيك توك",
                rate: {res['tiktok_likes']['rate']}, min: {res['tiktok_likes']['min']}, max: {res['tiktok_likes']['max']},
                unit: 1000, badge: "👍 سريع", speed: "⚡ فوري",
                label: "رابط المنشور (Video Link)", placeholder: "https://tiktok.com/@user/video/xxx", type: "standard"
            }},
            {{
                id: "tiktok-views", numId: {res['tiktok_views']['service']},
                name: "[{res['tiktok_views']['service']}] مشاهدات تيك توك",
                rate: {res['tiktok_views']['rate']}, min: {res['tiktok_views']['min']}, max: {res['tiktok_views']['max']},
                unit: 1000, badge: "🔥 الأكثر طلباً", speed: "🚀 فوري",
                label: "رابط المنشور (Video Link)", placeholder: "https://tiktok.com/@user/video/xxx", type: "standard"
            }}
        ]
    }},
    {{
        id: "telegram", name: "تيليجرام", desc: "أعضاء • مشاهدات",
        icon: "fab fa-telegram-plane", iconClass: "icon-telegram", category: "messaging", popular: false,
        services: [
            {{
                id: "tele-members", numId: {res['tele_members']['service']},
                name: "[{res['tele_members']['service']}] أعضاء تيليجرام (قنوات/كروبات)",
                rate: {res['tele_members']['rate']}, min: {res['tele_members']['min']}, max: {res['tele_members']['max']},
                unit: 1000, badge: "🛡️ آمن", speed: "⚡ سريع",
                label: "رابط القناة (Channel Link)", placeholder: "https://t.me/channel_name", type: "standard"
            }},
            {{
                id: "tele-views", numId: {res['tele_views']['service']},
                name: "[{res['tele_views']['service']}] مشاهدات تيليجرام (آخر منشور)",
                rate: {res['tele_views']['rate']}, min: {res['tele_views']['min']}, max: {res['tele_views']['max']},
                unit: 1000, badge: "👀 رخيص جداً", speed: "🚀 فوري",
                label: "رابط المنشور (Post Link)", placeholder: "https://t.me/channel/123", type: "standard"
            }}
        ]
    }}
];
'''

with open(r'c:\Users\حسين\Desktop\app\assets\js\config\servicesData.js', 'w', encoding='utf-8') as f:
    f.write(out_script)

print("SUCCESS: Updated servicesData.js with JAP exact IDs and Prices!")
