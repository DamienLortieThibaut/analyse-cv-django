#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from candidatures.views import CandidatureAnalyzeAPIView
from django.http import HttpRequest
from django.contrib.sessions.backends.db import SessionStore
import json

def test_api_directly():
    print("Test direct de l'API...")
    
    # Créer une requête simulée
    request = HttpRequest()
    request.method = 'POST'
    
    # Créer une session avec des données de test
    session = SessionStore()
    session['pending_candidature'] = {
        'email': 'test@example.com',
        'cv_text': '''Marie Dupont
Développeuse Python Senior
5 ans d'expérience en développement web
Compétences: Python, Django, JavaScript, React
Formation: Master en Informatique''',
        'cv_file_url': '#text-cv-test',
        'uploaded_at': '2024-01-01T00:00:00Z'
    }
    session.save()
    request.session = session
    
    # Appeler directement la vue API
    view = CandidatureAnalyzeAPIView()
    response = view.post(request)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.content.decode())
        print("Reponse API:")
        print(f"  Status: {data.get('status')}")
        if data.get('status') == 'success':
            candidate = data.get('candidate', {})
            experience = data.get('experience', {})
            scoring = data.get('scoring', {})
            print(f"  Full Name: {candidate.get('full_name')}")
            print(f"  Headline: {candidate.get('headline')}")
            print(f"  Score: {scoring.get('fit_score_overall')}")
            print(f"  Experience: {experience.get('years_total')} ans")
            print(f"  Experiences count: {len(experience.get('experiences', []))}")
            print("API fonctionne correctement avec structure enrichie!")
        else:
            print(f"  Erreur: {data.get('message')}")
    else:
        print(f"Erreur: {response.content.decode()}")

if __name__ == "__main__":
    test_api_directly()