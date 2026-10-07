import os

base_dir = r"c:\Users\حسين\Desktop\app"

# 1. Update index.html
html_path = os.path.join(base_dir, "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

sidebar_html = """
    <!-- Sidebar Drawer (المزيد) -->
    <div id="sidebar-drawer" class="sidebar-backdrop" onclick="window.StoreApp.UI.Sidebar.close(event)">
        <div class="sidebar-content" onclick="event.stopPropagation()">
            <div class="sidebar-header">
                <div class="sidebar-brand">
                    <div class="brand-icon"><i class="fas fa-chart-bar text-primary"></i></div>
                    <div class="brand-text">
                        <div class="brand-name">متجر الرشق</div>
                        <div class="brand-sub">خدمات السوشيال ميديا</div>
                    </div>
                </div>
                <button type="button" class="sidebar-close" onclick="window.StoreApp.UI.Sidebar.close()"><i class="fas fa-times"></i></button>
            </div>

            <div class="sidebar-user-card">
                <div class="user-avatar" id="sidebar-avatar">م</div>
                <div class="user-info">
                    <div class="user-name" id="sidebar-name">مستخدم</div>
                    <div class="user-id" onclick="window.StoreApp.Utils.Formatters.copyText(document.getElementById('sidebar-uid').innerText)" title="نسخ المعرف">
                        <i class="far fa-copy"></i> <span id="sidebar-uid">000000</span>
                    </div>
                </div>
            </div>

            <div class="sidebar-balance-card">
                <div class="balance-labels">
                    <div class="bal-title">الرصيد المتاح</div>
                    <div class="bal-amount" id="sidebar-balance">$0.00</div>
                </div>
                <button class="btn-charge" onclick="window.StoreApp.UI.Sidebar.close(); window.StoreApp.UI.Navigation.navigateTo('page-recharge')">
                    + شحن الرصيد
                </button>
            </div>

            <div class="sidebar-menu">
                <div class="menu-section-title">القوائم</div>
                <div class="menu-item" onclick="window.StoreApp.UI.Sidebar.close(); window.StoreApp.UI.Navigation.navigateTo('page-home')">
                    <i class="fas fa-th-large"></i><span>الرئيسية</span>
                    <i class="fas fa-chevron-left arrow-left"></i>
                </div>
                <div class="menu-item" onclick="window.StoreApp.UI.Sidebar.close(); window.StoreApp.UI.Navigation.navigateTo('page-orders')">
                    <i class="fas fa-box"></i><span>طلباتي</span>
                </div>
                <div class="menu-item" onclick="window.StoreApp.UI.Sidebar.close(); window.StoreApp.UI.Navigation.navigateTo('page-notifications')">
                    <i class="far fa-bell"></i><span>الإشعارات</span>
                </div>

                <div class="menu-section-title">الرصيد</div>
                <div class="menu-item" onclick="window.StoreApp.UI.Sidebar.close(); window.StoreApp.UI.Navigation.navigateTo('page-recharge')">
                    <i class="fas fa-wallet"></i><span>إضافة رصيد</span>
                </div>

                <div class="menu-section-title">المساعدة</div>
                <div class="menu-item" onclick="window.open('https://t.me/h99lh', '_blank')">
                    <i class="fas fa-headset"></i><span>الدعم الفني</span>
                </div>
            </div>

            <div class="sidebar-footer">
                <div class="menu-item logout" onclick="window.Telegram.WebApp.close()">
                    <i class="fas fa-sign-out-alt"></i><span>تسجيل الخروج</span>
                </div>
            </div>
        </div>
    </div>
"""

old_nav = """    <nav class="bottom-nav">
        <div class="nav-item active" onclick="window.StoreApp.UI.Navigation.navigateTo('page-home', this)">
            <i class="fas fa-home"></i>
            <span>الرئيسية</span>
        </div>
        <div class="nav-item" onclick="window.StoreApp.UI.Navigation.navigateTo('page-orders', this)">
            <i class="fas fa-list-alt"></i>
            <span>طلباتي</span>
        </div>
        <div class="nav-item" onclick="window.StoreApp.UI.Navigation.navigateTo('page-recharge', this)">
            <i class="fas fa-wallet"></i>
            <span>شحن</span>
        </div>
        <div class="nav-item" onclick="window.StoreApp.UI.Navigation.navigateTo('page-notifications', this)">
            <i class="fas fa-bell"></i>
            <span>الإشعارات</span>
            <span class="nav-badge" id="bottom-nav-notif-badge" style="display: none;">0</span>
        </div>
    </nav>"""

new_nav = """    <nav class="bottom-nav">
        <div class="nav-item active" onclick="window.StoreApp.UI.Navigation.navigateTo('page-home', this)">
            <i class="fas fa-home"></i>
            <span>الرئيسية</span>
        </div>
        <div class="nav-item" onclick="window.StoreApp.UI.Navigation.navigateTo('page-orders', this)">
            <i class="fas fa-list-alt"></i>
            <span>طلباتي</span>
        </div>
        <div class="nav-item" onclick="window.StoreApp.UI.Navigation.navigateTo('page-recharge', this)">
            <i class="fas fa-wallet"></i>
            <span>شحن</span>
        </div>
        <div class="nav-item" onclick="window.StoreApp.UI.Navigation.navigateTo('page-notifications', this)">
            <i class="fas fa-bell"></i>
            <span>الإشعارات</span>
            <span class="nav-badge" id="bottom-nav-notif-badge" style="display: none;">0</span>
        </div>
        <div class="nav-item" onclick="window.StoreApp.UI.Sidebar.open()">
            <i class="fas fa-bars"></i>
            <span>المزيد</span>
        </div>
    </nav>"""

if 'id="sidebar-drawer"' not in html:
    html = html.replace(old_nav, new_nav)
    html = html.replace('<!-- Universal Modal Dialog -->', sidebar_html + '\n    <!-- Universal Modal Dialog -->')
    html = html.replace('<!-- 4. طبقة واجهة المستخدم (UI Layer) -->', '<!-- 4. طبقة واجهة المستخدم (UI Layer) -->\n    <script src="assets/js/ui/sidebar.js"></script>')
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


# 2. Add Sidebar JS
sidebar_js = """
window.StoreApp = window.StoreApp || {};
window.StoreApp.UI = window.StoreApp.UI || {};

window.StoreApp.UI.Sidebar = (function() {
    'use strict';

    let sidebarEl = null;

    function init() {
        if (!sidebarEl) {
            sidebarEl = document.getElementById('sidebar-drawer');
        }
    }

    function open() {
        init();
        if (!sidebarEl) return;
        
        // Update user data dynamically
        const user = window.StoreApp.Services.Telegram.getUser() || { id: 0, first_name: 'مستخدم', username: '' };
        const bal = window.StoreApp.Services.Storage.getBalance();
        
        const fname = user.first_name || 'مستخدم';
        document.getElementById('sidebar-name').innerText = fname;
        document.getElementById('sidebar-avatar').innerText = fname.charAt(0);
        document.getElementById('sidebar-uid').innerText = user.username || user.id;
        document.getElementById('sidebar-balance').innerText = '$' + parseFloat(bal).toFixed(4);

        sidebarEl.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function close(e) {
        if (e && e.target !== e.currentTarget) return; // Prevent closing when clicking content
        init();
        if (!sidebarEl) return;
        sidebarEl.classList.remove('active');
        document.body.style.overflow = '';
    }

    return { init, open, close };
})();
"""
os.makedirs(os.path.join(base_dir, "assets", "js", "ui"), exist_ok=True)
with open(os.path.join(base_dir, "assets", "js", "ui", "sidebar.js"), "w", encoding="utf-8") as f:
    f.write(sidebar_js)


# 3. Add CSS
css_path = os.path.join(base_dir, "assets", "css", "layout.css")
with open(css_path, "a", encoding="utf-8") as f:
    f.write("""
/* ==================== Sidebar Drawer ==================== */
.sidebar-backdrop {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(0,0,0,0.6);
    z-index: 10000;
    opacity: 0; visibility: hidden;
    transition: all 0.3s ease;
    backdrop-filter: blur(3px);
}
.sidebar-backdrop.active {
    opacity: 1; visibility: visible;
}
.sidebar-content {
    position: absolute; top: 0; right: -300px;
    width: 280px; height: 100%;
    background-color: var(--bg-main);
    box-shadow: -4px 0 15px rgba(0,0,0,0.15);
    transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex; flex-direction: column;
    overflow-y: auto;
    border-top-left-radius: var(--radius-xl);
    border-bottom-left-radius: var(--radius-xl);
}
.sidebar-backdrop.active .sidebar-content { right: 0; }
.sidebar-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px; border-bottom: 1px solid var(--border-color);
}
.sidebar-brand { display: flex; align-items: center; gap: 12px; }
.sidebar-brand .brand-icon {
    width: 36px; height: 36px; background: var(--primary-bg);
    border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.sidebar-brand .brand-name { font-weight: 800; font-size: 15px; color: var(--text-main); }
.sidebar-brand .brand-sub { font-size: 11px; color: var(--text-muted); }
.sidebar-close {
    background: var(--bg-input); border: none;
    width: 30px; height: 30px; border-radius: var(--radius-full);
    display: flex; align-items: center; justify-content: center;
    color: var(--text-muted); cursor: pointer;
}
.sidebar-user-card {
    display: flex; align-items: center; gap: 12px; padding: 15px;
    background: var(--bg-card); margin: 15px; border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm); border: 1px solid var(--border-color-light);
}
.user-avatar {
    width: 45px; height: 45px; background: var(--primary-gradient); color: white;
    border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 800;
}
.user-info .user-name { font-weight: 700; font-size: 15px; color: var(--text-main); margin-bottom: 2px; }
.user-info .user-id { font-size: 12px; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; gap:4px; }
.sidebar-balance-card {
    background: var(--bg-card); padding: 15px; margin: 0 15px 15px;
    border-radius: var(--radius-md); box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color-light); display: flex; flex-direction: column; gap: 12px;
}
.balance-labels .bal-title { font-size: 12px; color: var(--text-muted); }
.balance-labels .bal-amount { font-size: 22px; font-weight: 900; color: var(--text-main); }
.btn-charge {
    background: var(--primary-gradient); color: white; border: none;
    padding: 10px; border-radius: var(--radius-sm); font-weight: 700;
    cursor: pointer; text-align: center; width: 100%;
}
.sidebar-menu { padding: 5px 15px; flex-grow: 1; }
.menu-section-title { font-size: 11px; font-weight: 800; color: var(--text-dim); margin: 15px 0 8px; padding-right: 5px; }
.sidebar-menu .menu-item {
    display: flex; align-items: center; gap: 12px; padding: 12px 10px;
    border-radius: var(--radius-sm); color: var(--text-main); font-weight: 700; font-size: 14px;
    cursor: pointer; transition: var(--transition-fast); margin-bottom: 2px;
}
.sidebar-menu .menu-item i { width: 18px; text-align: center; color: var(--text-muted); }
.sidebar-menu .menu-item:hover, .sidebar-menu .menu-item.active { background: var(--bg-card-hover); color: var(--primary); }
.sidebar-menu .menu-item:hover i, .sidebar-menu .menu-item.active i { color: var(--primary); }
.arrow-left { margin-right: auto; font-size: 10px; color: var(--text-dim); }
.sidebar-footer { padding: 15px; border-top: 1px solid var(--border-color); }
.sidebar-footer .menu-item {
    display: flex; align-items: center; gap: 12px; padding: 12px;
    border-radius: var(--radius-sm); font-weight: 700; cursor: pointer; color: var(--danger);
}
.sidebar-footer .menu-item i { color: var(--danger); width: 18px; text-align: center; }
.sidebar-footer .menu-item:hover { background: var(--danger-bg); }
""")
print("Frontend patch successful")
