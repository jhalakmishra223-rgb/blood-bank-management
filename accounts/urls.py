from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.home, name='home'),
    path('donors/', views.donors, name='donors'),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("change-password/", views.change_password, name="change_password"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("contact/", views.contact, name="contact"),
    path(
    'forgot-password/',auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'),name='password_reset'),
    path(
    'forgot-password/done/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ),name='password_reset_done'),
    path(
    'reset-password/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ),
    name='password_reset_confirm'
),

    path(
    'reset-password/complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),
]