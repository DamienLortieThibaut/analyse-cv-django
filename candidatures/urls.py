from django.urls import path
from .views import (
    CandidatureUploadView,
    CandidatureTestTextView,
    CandidatureAnalyzeView,
    CandidatureAnalyzeAPIView,
    CandidatureSuccessView,
    CandidatureListView
)

app_name = 'candidatures'

urlpatterns = [
    path('', CandidatureUploadView.as_view(), name='index'),
    path('new/', CandidatureUploadView.as_view(), name='upload'),
    path('upload/', CandidatureUploadView.as_view(), name='upload'),
    path('test-text/', CandidatureTestTextView.as_view(), name='test-text'),
    path('analyze/', CandidatureAnalyzeView.as_view(), name='analyze'),
    path('api/analyze/', CandidatureAnalyzeAPIView.as_view(), name='analyze-api'),
    path('list/', CandidatureListView.as_view(), name='list'),

    # Liste des candidatures filtré par id
    path('list/id/<str:id>/', CandidatureListView.as_view(), name='list-id'),

    path('<uuid:candidature_id>/', CandidatureSuccessView.as_view(), name='success'),
    path('<uuid:pk>/', CandidatureSuccessView.as_view(), name='detail'),
    path('<uuid:pk>/delete/', CandidatureUploadView.as_view(), name='delete'),
]