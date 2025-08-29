#!/usr/bin/env python
"""
Test de l'API d'analyse avec session simulée d'upload PDF
"""
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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

def test_pdf_api_with_session():
    """Test de l'API avec une session PDF simulée"""
    print("=== Test API avec Session PDF Simulee ===")
    
    # Créer un fichier factice dans le storage
    fake_pdf_content = b"Fake PDF content for testing"  # Pas un vrai PDF, juste pour test
    file_path = "cvs/Damien_LORTIE-THIBAUT_CV.pdf"
    
    try:
        # Sauvegarder le fichier factice
        saved_path = default_storage.save(file_path, ContentFile(fake_pdf_content))
        print(f"Fichier test sauvegarde: {saved_path}")
        
        # Créer une requête simulée
        request = HttpRequest()
        request.method = 'POST'
        
        # Créer une session avec des données d'upload PDF
        session = SessionStore()
        session['pending_candidature'] = {
            'email': 'test@example.com',
            'cv_file_path': saved_path,  # Chemin du fichier uploadé
            'cv_file_url': f'http://example.com/media/{saved_path}',
            'uploaded_at': '2024-01-01T00:00:00Z'
        }
        session.save()
        request.session = session
        
        print(f"Session creee avec cv_file_path: {saved_path}")
        
        # Appeler l'API
        view = CandidatureAnalyzeAPIView()
        response = view.post(request)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            print("Reponse API:")
            print(f"  Status: {data.get('status')}")
            if data.get('status') == 'success':
                analysis = data.get('analysis', {})
                print(f"  Headline: {analysis.get('headline')}")
                print(f"  Score: {analysis.get('fit_score')}")
                print("API PDF fonctionne!")
                success = True
            else:
                print(f"  Erreur: {data.get('message')}")
                success = False
        else:
            print(f"Erreur HTTP: {response.content.decode()}")
            success = False
            
        # Nettoyer le fichier de test
        try:
            default_storage.delete(saved_path)
            print("Fichier test nettoye")
        except:
            pass
            
        return success
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_api_with_session()
    print(f"\nResultat: {'SUCCESS' if success else 'FAILED'}")