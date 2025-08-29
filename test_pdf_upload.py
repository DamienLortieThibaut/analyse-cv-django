#!/usr/bin/env python
"""
Test du workflow d'upload PDF complet
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
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from candidatures.services import CVAnalysisService

def create_dummy_pdf():
    """Créer un PDF factice avec du texte"""
    # Pour ce test, on va créer un contenu qui ressemble à un PDF mais qui est juste du texte
    # En réalité, il faudrait un vrai PDF, mais pour le test on simule
    content = """
Marie Dupont
Développeuse Python Senior
Email: marie.dupont@email.com

EXPÉRIENCE
- Senior Developer chez TechCorp (2020-2024)
- Développement Django et React

FORMATION  
- Master Informatique (2018-2020)

COMPÉTENCES
- Python, Django, JavaScript, React
- Git, Docker, PostgreSQL
"""
    return content.encode('utf-8')

def test_pdf_analysis_service():
    """Test du service d'analyse PDF"""
    print("=== Test du Service d'Analyse PDF ===")
    
    service = CVAnalysisService()
    pdf_content = create_dummy_pdf()
    
    try:
        print("Test d'analyse des bytes PDF...")
        result, model_version = service.analyze_cv_from_bytes(pdf_content)
        
        print(f"✅ Analyse réussie!")
        print(f"Modèle: {model_version}")
        print(f"Nom: {result.first_name} {result.last_name}")
        print(f"Titre: {result.headline}")
        print(f"Score: {result.fit_score_overall}/100")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_pdf_upload_workflow():
    """Test du workflow complet d'upload PDF"""
    print("\n=== Test Workflow Upload PDF ===")
    
    client = Client()
    
    # 1. Créer un fichier PDF factice
    pdf_content = create_dummy_pdf()
    uploaded_file = SimpleUploadedFile(
        name='test_cv.pdf',
        content=pdf_content,
        content_type='application/pdf'
    )
    
    # 2. Simuler l'upload
    print("1. Test d'upload PDF...")
    upload_data = {
        'email': 'test@example.com',
        'cv_file': uploaded_file
    }
    
    try:
        response = client.post('/candidatures/upload/', upload_data)
        print(f"   Status upload: {response.status_code}")
        
        if response.status_code == 302:  # Redirect vers analyze
            print("   ✅ Upload réussi, redirection vers analyze")
            
            # Récupérer la session
            session_key = client.cookies.get('sessionid')
            if session_key:
                from django.contrib.sessions.backends.db import SessionStore
                session = SessionStore(session_key=session_key.value)
                session_data = session.get('pending_candidature')
                print(f"   Session créée: {list(session_data.keys()) if session_data else 'Aucune donnée'}")
                
                if session_data and 'cv_file_path' in session_data:
                    print(f"   ✅ Fichier sauvegardé: {session_data['cv_file_path']}")
                    
                    # 3. Test de l'API d'analyse
                    print("2. Test API d'analyse...")
                    api_response = client.post('/candidatures/api/analyze/', 
                                             content_type='application/json',
                                             HTTP_X_CSRFTOKEN='test-token')
                    
                    print(f"   Status API: {api_response.status_code}")
                    
                    if api_response.status_code == 200:
                        import json
                        data = api_response.json()
                        print(f"   ✅ API Response: {data.get('status')}")
                        
                        if data.get('status') == 'success':
                            analysis = data.get('analysis', {})
                            print(f"   - Candidat: {analysis.get('headline', 'N/A')}")
                            print(f"   - Score: {analysis.get('fit_score', 'N/A')}/100")
                            return True
                        else:
                            print(f"   ❌ Erreur analyse: {data.get('message')}")
                    else:
                        print(f"   ❌ Erreur API: {api_response.content.decode()}")
                else:
                    print("   ❌ Session mal créée")
            else:
                print("   ❌ Pas de session")
        else:
            print(f"   ❌ Erreur upload: {response.content.decode()}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    print("Test du workflow PDF complet...\n")
    
    # Test 1: Service direct
    service_ok = test_pdf_analysis_service()
    
    # Test 2: Workflow complet
    workflow_ok = test_pdf_upload_workflow()
    
    print(f"\n=== Résultats ===")
    print(f"Service PDF: {'✅' if service_ok else '❌'}")
    print(f"Workflow PDF: {'✅' if workflow_ok else '❌'}")
    
    if service_ok and workflow_ok:
        print("🎉 Workflow PDF fonctionnel!")
    else:
        print("⚠️ Problème détecté dans le workflow PDF")