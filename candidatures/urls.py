from django.urls import path
from .views import (
    CandidatureUploadView,
    CandidatureTestTextView,
    CandidatureAnalyzeView,
    CandidatureAnalyzeAPIView,
    CandidatureSuccessView
)

app_name = 'candidatures'

urlpatterns = [
    path('', CandidatureUploadView.as_view(), name='upload'),
    path('upload/', CandidatureUploadView.as_view(), name='upload'),
    path('test-text/', CandidatureTestTextView.as_view(), name='test-text'),
    path('analyze/', CandidatureAnalyzeView.as_view(), name='analyze'),
    path('api/analyze/', CandidatureAnalyzeAPIView.as_view(), name='analyze-api'),
    path('<uuid:candidature_id>/', CandidatureSuccessView.as_view(), name='success'),
]