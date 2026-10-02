JAZZMIN_SETTINGS = {
    # =========================================================
    # 1. BRANDING & TITLES
    # =========================================================

    "site_title": "Global Wealth University Admin",
    "site_header": "Global Wealth University",
    "site_brand": "Global Wealth University",
    "welcome_sign": "Welcome to Global Wealth University",
    "copyright": "Global Wealth University",


    # =========================================================
    # 2. LOGO CONFIGURATION
    # =========================================================

    "site_logo": "img/Global-wealth-university.PNG",
    "site_logo_classes": "brand-image",
    # "login_logo": "img/Global-wealth-university.PNG",
    # "login_logo_classes": "login-logo-img",


    # =========================================================
    # 3. CUSTOM CSS & JS
    # =========================================================

    "custom_css": "css/my_jazzmin.css",
    "custom_js": "js/my_jazzmin.js",


    # =========================================================
    # 4. USER AVATAR - DISABLED
    # =========================================================

    # "user_avatar": "profile.avatar",  # REMOVED - was causing issues


    # =========================================================
    # 5. TOP MENU LINKS
    # =========================================================

    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {
            "name": "Support",
            "url": "https://github.com/farridav/django-jazzmin/issues",
            "new_window": True
        },
        {"model": "auth.User"},
        {"app": "books"},
    ],


    # =========================================================
    # 6. USER MENU LINKS
    # =========================================================

    "usermenu_links": [
        {
            "name": "Support",
            "url": "https://github.com/farridav/django-jazzmin/issues",
            "new_window": True
        },
        {"model": "auth.user"}
    ],


    # =========================================================
    # 7. SIDE MENU CONFIGURATION
    # =========================================================

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],


    # =========================================================
    # 8. CUSTOM LINKS
    # =========================================================

    "custom_links": {
        "books": [{
            "name": "Make Messages",
            "url": "make_messages",
            "icon": "fas fa-comments",
            "permissions": ["books.view_book"]
        }]
    },


    # =========================================================
    # 9. ICONS
    # =========================================================

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",


    # =========================================================
    # 10. SEARCH & RELATED MODALS
    # =========================================================

    "search_model": ["auth.User", "auth.Group"],
    "related_modal_active": True,


    # =========================================================
    # 11. UI TWEAKS
    # =========================================================

    "use_google_fonts_cdn": True,

    "show_ui_builder": False,


    # =========================================================
    # 12. CHANGE VIEW FORMAT
    # =========================================================

    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs"
    },
}