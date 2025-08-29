from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('list/', views.list_candidatures, name='list'),
    path('home/email/<str:email>/', views.home, name='home-email'),
    path('api/data/', views.dashboard_data_api, name='data-api'),
]
