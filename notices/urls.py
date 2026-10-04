from django.urls import path
from . import views


urlpatterns = [
    # ---------- STUDENT ----------
    path('', views.dashboard, name='dashboard'),
    path('pinned/', views.pinned_notices, name='pinned_notices'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),

    # ---------- API ----------
    path('api/notices/search/', views.api_search_notices, name='api_search_notices'),

    # ---------- ADMIN ----------
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/notices/', views.manage_notices, name='manage_notices'),
    path('admin-panel/notices/new/', views.notice_create, name='notice_create'),
    path('admin-panel/notices/<int:pk>/edit/', views.notice_edit, name='notice_edit'),
    path('admin-panel/notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),
    path('admin-panel/notices/<int:pk>/toggle/', views.notice_toggle_publish, name='notice_toggle_publish'),

    # ---------- CATEGORIES ----------
    path('admin-panel/categories/', views.category_list, name='category_list'),
    path('admin-panel/categories/new/', views.category_create, name='category_create'),
    path('admin-panel/categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('admin-panel/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]