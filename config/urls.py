from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.static import serve


urlpatterns = [
    # ============================================
    # Password Reset (Django native — allauth bug workaround)
    # ============================================
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='account/password_reset_form.html',
             email_template_name='account/password_reset_email.txt',
             subject_template_name='account/password_reset_subject.txt',
             success_url='/password-reset/done/',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='account/password_reset_confirm.html',
             success_url='/password-reset/complete/',
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='account/password_reset_complete.html',
         ),
         name='password_reset_complete'),

    # ============================================
    # Django built-in admin (backup / advanced)
    # ============================================
    path('django-admin/', admin.site.urls),

    # ============================================
    # django-allauth — login, signup, logout, Google OAuth, email verify
    # ============================================
    path('accounts/', include('allauth.urls')),

    # ============================================
    # Our custom app (notice board)
    # ============================================
    path('', include('notices.urls')),

    # ============================================
    # Media files — served in BOTH dev & production
    # (fixes attachment download on Render)
    # ============================================
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]


# Static files — WhiteNoise handles production, this na for local dev
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)