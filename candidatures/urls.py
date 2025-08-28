from django.urls import path
from . import views

app_name = 'candidatures'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.list_candidatures, name='list'),
    path('<int:pk>/', views.detail_candidature, name='detail'),
    path('<int:pk>/delete/', views.delete_candidature, name='delete'),
]
