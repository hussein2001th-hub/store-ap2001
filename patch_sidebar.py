import os

html_path = r'c:\Users\حسين\Desktop\app\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

sidebar_html = """
    <!-- Sidebar Drawer -->
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

if 'id="sidebar-drawer"' not in html:
    html = html.replace('<div id="app-modal"', sidebar_html + '\n    <div id="app-modal"')
    
    if '<script src="assets/js/ui/sidebar.js"></script>' not in html:
        html = html.replace('<script src="assets/js/ui/renderers.js"></script>', '<script src="assets/js/ui/renderers.js"></script>\n    <script src="assets/js/ui/sidebar.js"></script>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Sidebar injected!')
else:
    print('Sidebar already exists.')
