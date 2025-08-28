from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('list/', views.list_candidatures, name='list'),
]
