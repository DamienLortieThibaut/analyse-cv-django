#!/usr/bin/env python
"""
Test de la réponse API complète avec toutes les données
"""
import os
import sys
import django
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from candidatures.views import CandidatureAnalyzeAPIView
from django.http import HttpRequest
from django.contrib.sessions.backends.db import SessionStore

def test_full_response():
    print("=== Test Reponse API Complete ===")
    
    # Créer une requête simulée avec CV plus riche
    request = HttpRequest()
    request.method = 'POST'
    
    # CV de test plus détaillé
    rich_cv = """
    Jean Dupont
    Développeur Full-Stack Senior
    Email: jean.dupont@email.com
    Téléphone: 01 23 45 67 89
    
    RÉSUMÉ PROFESSIONNEL
    Développeur expérimenté avec 8 ans d'expérience en développement web moderne.
    Expert en JavaScript, Python et technologies cloud. Passionné par l'innovation
    et les bonnes pratiques de développement.
    
    EXPÉRIENCE PROFESSIONNELLE
    
    Senior Developer - TechCorp (2020-2024)
    • Développement d'applications React/Node.js
    • Architecture microservices avec Docker et Kubernetes
    • Encadrement d'une équipe de 5 développeurs
    • Mise en place CI/CD et bonnes pratiques DevOps
    
    Développeur Full-Stack - StartupXYZ (2017-2020)
    • Développement d'une plateforme e-commerce en Django
    • Intégration APIs de paiement (Stripe, PayPal)
    • Optimisation performance et SEO
    
    Développeur Junior - WebAgency (2016-2017)
    • Développement sites web WordPress et PHP
    • Maintenance et support client
    
    FORMATION
    Master Informatique - Université Paris-Saclay (2014-2016)
    • Spécialisation Intelligence Artificielle
    • Projet de fin d'études: Système de recommandation ML
    
    Licence Informatique - Université de Versailles (2011-2014)
    • Major de promotion
    • Stage de 6 mois chez IBM
    
    COMPÉTENCES TECHNIQUES
    - Frontend: JavaScript, React, Vue.js, Angular, HTML5, CSS3, Sass
    - Backend: Python, Django, Node.js, Express, PHP, Laravel
    - Bases de données: PostgreSQL, MongoDB, Redis, MySQL
    - Cloud: AWS, Azure, Docker, Kubernetes, Terraform
    - Outils: Git, Jenkins, Webpack, Jest, Cypress
    
    LANGUES
    - Français: Natif
    - Anglais: Courant (TOEIC 950)
    - Espagnol: Intermédiaire (niveau B2)
    - Allemand: Notions (niveau A2)
    
    CENTRES D'INTÉRÊT
    - Open Source (contributeur sur GitHub)
    - Photographie et voyage
    - Sport: Course à pied, escalade
    - Lecture technique et veille technologique
    
    INFORMATIONS COMPLÉMENTAIRES
    - Disponible immédiatement
    - Prétentions salariales: 55-65k€
    - Mobilité: France, Remote OK
    - Permis B, véhicule personnel
    """
    
    # Créer une session avec des données de test
    session = SessionStore()
    session['pending_candidature'] = {
        'email': 'jean.dupont@email.com',
        'cv_text': rich_cv,
        'cv_file_url': '#text-cv-rich-test',
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
        print("Structure de donnees complete:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Erreur: {response.content.decode()}")

if __name__ == "__main__":
    test_full_response()