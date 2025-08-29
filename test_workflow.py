#!/usr/bin/env python
"""
Test complet du workflow d'analyse de CV
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from django.test import Client
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
import json

def test_upload_and_analysis_workflow():
    """Test du workflow complet : Upload -> Analyse -> Résultat"""
    
    print("=== Test du Workflow Complet ===")
    
    client = Client()
    
    # 1. Test de la page d'upload
    print("1. Test de la page d'upload...")
    response = client.get('/candidatures/upload/')
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200, "Page d'upload inaccessible"
    print("   ✅ Page d'upload accessible")
    
    # 2. Test d'upload de texte (simulation)
    print("2. Simulation d'upload de texte...")
    upload_data = {
        'email': 'test@example.com',
        'cv_text': '''
        Marie Dupont
        Développeuse Python Senior
        Email: marie.dupont@email.com
        
        EXPÉRIENCE
        - Senior Developer chez TechCorp (2020-2024)
        - Développement d'applications Django et React
        - Gestion d'équipe de 3 développeurs
        
        FORMATION
        - Master Informatique, Université Paris-Saclay (2018-2020)
        
        COMPÉTENCES
        - Python, Django, JavaScript, React, PostgreSQL
        - Git, Docker, AWS
        
        LANGUES
        - Français: Natif
        - Anglais: Courant (B2)
        '''
    }
    
    # Simuler l'upload via test-text
    response = client.post('/candidatures/test-text/', upload_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 302:  # Redirect vers analyze
        print("   ✅ Upload réussi, redirection vers analyze")
        # Récupérer la session
        session_key = client.cookies.get('sessionid')
        if session_key:
            session = SessionStore(session_key=session_key.value)
            session_data = session.get('pending_candidature')
            print(f"   Session créée avec: {list(session_data.keys()) if session_data else 'Aucune donnée'}")
        else:
            print("   ⚠️ Pas de session créée")
    else:
        print(f"   ❌ Erreur d'upload: {response.content.decode()}")
        return False
    
    # 3. Test de la page d'analyse
    print("3. Test de la page d'analyse...")
    response = client.get('/candidatures/analyze/')
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200, "Page d'analyse inaccessible"
    print("   ✅ Page d'analyse accessible")
    
    # 4. Test de l'API d'analyse
    print("4. Test de l'API d'analyse...")
    
    # Créer une nouvelle session pour l'API
    if not client.cookies.get('sessionid'):
        # Recréer manuellement la session si nécessaire
        session = SessionStore()
        session['pending_candidature'] = {
            'email': 'test@example.com',
            'cv_text': upload_data['cv_text'],
            'cv_file_url': '#text-cv-test',
            'uploaded_at': '2024-01-01T00:00:00Z'
        }
        session.save()
        client.cookies['sessionid'] = session.session_key
    
    # Appel de l'API
    response = client.post('/candidatures/analyze-api/', 
                         content_type='application/json',
                         HTTP_X_CSRFTOKEN='test-token')
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ API Response: {data.get('status', 'unknown')}")
            
            if data.get('status') == 'success':
                analysis = data.get('analysis', {})
                print(f"   - Candidat: {analysis.get('headline', 'N/A')}")
                print(f"   - Score: {analysis.get('fit_score', 'N/A')}/100")
                print(f"   - Expérience: {analysis.get('years_experience', 'N/A')} ans")
                print(f"   - Compétences: {analysis.get('skills_primary', [])[:3]}")
                print(f"   - Redirect: {data.get('redirect_url', 'N/A')}")
                return True
            else:
                print(f"   ❌ Erreur analyse: {data.get('message', 'Inconnue')}")
                return False
        except json.JSONDecodeError:
            print(f"   ❌ Réponse API invalide: {response.content.decode()}")
            return False
    else:
        print(f"   ❌ Erreur API: {response.content.decode()}")
        return False

def test_urls():
    """Test de toutes les URLs importantes"""
    print("\n=== Test des URLs ===")
    
    client = Client()
    urls_to_test = [
        ('/candidatures/', 'Index candidatures'),
        ('/candidatures/upload/', 'Page upload'),
        ('/candidatures/test-text/', 'Page test texte'),
        ('/candidatures/analyze/', 'Page analyse'),
    ]
    
    for url, description in urls_to_test:
        try:
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Erreur - {str(e)}")

if __name__ == "__main__":
    print("Démarrage du test du workflow complet...\n")
    
    try:
        # Test des URLs
        test_urls()
        
        # Test du workflow complet
        success = test_upload_and_analysis_workflow()
        
        print(f"\n=== Résultat Final ===")
        if success:
            print("🎉 Workflow complet fonctionnel!")
            print("✅ Upload → Analyse → API → Résultat")
        else:
            print("❌ Problème détecté dans le workflow")
            
    except Exception as e:
        print(f"❌ Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()