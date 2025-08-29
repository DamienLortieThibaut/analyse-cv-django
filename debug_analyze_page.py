#!/usr/bin/env python
"""
Debug de la page d'analyse
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from django.test import Client
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse

def test_analyze_page_with_session():
    """Test de la page analyze avec session"""
    print("=== Debug Page Analyze ===")
    
    client = Client()
    
    # 1. Créer une session avec des données d'upload
    session = SessionStore()
    session['pending_candidature'] = {
        'email': 'kilian@cashflowpositif.fr',
        'cv_file_path': 'cvs/Damien_LORTIE-THIBAUT_CV.pdf',
        'cv_file_url': 'http://example.com/media/cvs/test.pdf',
        'uploaded_at': '2024-01-01T00:00:00Z'
    }
    session.save()
    
    print(f"Session creee: {session.session_key}")
    
    # 2. Faire la requete avec la session
    client.cookies['sessionid'] = session.session_key
    response = client.get('/candidatures/analyze/')
    
    print(f"Status page analyze: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Chercher l'URL de l'API dans le contenu
        if 'api/analyze' in content:
            print("✅ URL API trouvee dans la page")
            # Extraire l'URL exacte
            import re
            url_match = re.search(r'fetch\("([^"]*api/analyze[^"]*)"', content)
            if url_match:
                api_url = url_match.group(1)
                print(f"URL API extraite: {api_url}")
            else:
                print("❌ Pattern fetch() non trouve")
        else:
            print("❌ URL API NON trouvee dans la page")
            
        # Chercher les données de candidature
        if 'candidature_data' in content:
            print("✅ candidature_data present dans le template")
        else:
            print("❌ candidature_data manquant")
            
        # Chercher les scripts JavaScript
        if 'Starting analysis' in content:
            print("✅ JavaScript d'analyse present")
        else:
            print("❌ JavaScript d'analyse manquant")
            
        # Vérifier la présence des éléments UI
        if 'analysisStatus' in content:
            print("✅ Elements UI presents")
        else:
            print("❌ Elements UI manquants")
    else:
        print(f"❌ Erreur page: {response.content.decode()}")

def test_api_url_reverse():
    """Test de génération d'URL"""
    print("\n=== Test Generation URL ===")
    
    try:
        api_url = reverse('candidatures:analyze-api')
        print(f"URL generee: {api_url}")
        
        # Tester l'URL directement
        client = Client()
        response = client.get(api_url)  # GET pour tester l'existence
        print(f"Status test URL: {response.status_code}")
        
        if response.status_code == 405:  # Method Not Allowed = URL existe
            print("✅ URL API accessible (405 = Method Not Allowed normal pour GET)")
        else:
            print(f"❌ Probleme URL: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur generation URL: {str(e)}")

if __name__ == "__main__":
    test_analyze_page_with_session()
    test_api_url_reverse()