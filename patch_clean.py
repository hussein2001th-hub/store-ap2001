import os

base_dir = r"c:\Users\حسين\Desktop\app"

# 1. Update index.html
html_path = os.path.join(base_dir, "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Remove "+ شحن حساب" button from top header area
html = html.replace('<button class="btn-charge" onclick="window.StoreApp.UI.Navigation.navigateTo(\'page-recharge\')">\n                        <i class="fas fa-plus"></i> شحن حساب\n                    </button>', '')

# Remove "+ شحن الرصيد" from sidebar (if it exists in index.html)
html = html.replace('<button class="btn-charge" onclick="window.StoreApp.UI.Sidebar.close(); window.StoreApp.UI.Navigation.navigateTo(\'page-recharge\')">\n                    + شحن الرصيد\n                </button>', '')
html = html.replace('<div class="menu-section-title">الرصيد</div>', '')
html = html.replace('<div class="menu-item" onclick="window.StoreApp.UI.Sidebar.close(); window.StoreApp.UI.Navigation.navigateTo(\'page-recharge\')">\n                    <i class="fas fa-wallet"></i><span>إضافة رصيد</span>\n                </div>', '')

# Remove from bottom nav
html = html.replace('<div class="nav-item" onclick="window.StoreApp.UI.Navigation.navigateTo(\'page-recharge\', this)">\n            <i class="fas fa-wallet"></i>\n            <span>شحن</span>\n        </div>', '')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)


# 2. Update renderers.js (Remove + 682)
renderers_path = os.path.join(base_dir, "assets", "js", "ui", "renderers.js")
with open(renderers_path, "r", encoding="utf-8") as f:
    r_js = f.read()
r_js = r_js.replace('const count = (state.orders ? state.orders.length : 0) + 682;', 'const count = (state.orders ? state.orders.length : 0);')
with open(renderers_path, "w", encoding="utf-8") as f:
    f.write(r_js)


# 3. Update storageService.js (Remove dummy data)
storage_path = os.path.join(base_dir, "assets", "js", "services", "storageService.js")
with open(storage_path, "r", encoding="utf-8") as f:
    s_js = f.read()

# We can just replace the INITIAL_STATE block
old_init_state = """    const INITIAL_STATE = {
        version: "2.6.0",
        balance: 3.12,
        orders: [
            {
                id: 984120,
                serviceId: "insta-followers-30d",
                service: "متابعين إنستغرام (حقيقي) - ضمان 30 يوم",
                platformName: "إنستغرام",
                target: "https://instagram.com/h99lh",
                qty: 1000,
                cost: 1.20,
                status: "مكتمل",
                date: "2026-09-25 14:20"
            },
            {
                id: 984121,
                serviceId: "insta-likes-fast",
                service: "لايكات إنستغرام (سريع جداً + فوري)",
                platformName: "إنستغرام",
                target: "https://instagram.com/p/C8xyz",
                qty: 500,
                cost: 0.18,
                status: "مكتمل",
                date: "2026-09-27 10:15"
            }
        ],
        notifications: [
            {
                id: 1,
                title: "مرحباً بك في متجر حسين أثير!",
                body: "تم تحديث واجهة المتجر بنجاح لمواكبة أحدث معايير السرعة والأمان مع دعم تليجرام الكامل.",
                time: "اليوم 12:00 م",
                read: false
            }
        ],
        theme: 'light'
    };"""

new_init_state = """    const INITIAL_STATE = {
        version: "2.7.0",
        balance: 0.0,
        orders: [],
        notifications: [
            {
                id: 1,
                title: "مرحباً بك في متجر حسين أثير!",
                body: "تم تحديث واجهة المتجر بنجاح لمواكبة أحدث معايير السرعة والأمان.",
                time: "اليوم 12:00 م",
                read: false
            }
        ],
        theme: 'light'
    };"""

if '984120' in s_js:
    s_js = s_js.replace(old_init_state, new_init_state)
    # Clear local storage script addition
    s_js = s_js.replace('function init() {', 'function init() { localStorage.removeItem(STORAGE_KEY); ')
    with open(storage_path, "w", encoding="utf-8") as f:
        f.write(s_js)

print("Patch clean stats successful")
