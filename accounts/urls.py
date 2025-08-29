from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard et profil
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Administration (pour les admins)
    path('admin/users/', views.admin_users, name='admin_users'),
]
