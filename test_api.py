#!/usr/bin/env python
"""
Script de test pour l'API d'analyse des CV
"""
import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from candidatures.services import CVAnalysisService
from django.conf import settings

def test_analysis_service():
    print("Test du service d'analyse des CV...")
    
    # Test 1: Configuration
    print(f"[OK] ANTHROPIC_API_KEY configure: {'Oui' if settings.ANTHROPIC_API_KEY else 'Non (mode mock)'}")
    print(f"[OK] Modele utilise: {settings.ANTHROPIC_MODEL}")
    
    # Test 2: Initialisation du service
    try:
        service = CVAnalysisService()
        print("[OK] Service CVAnalysisService initialise avec succes")
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'initialisation du service: {e}")
        return False
    
    # Test 3: Analyse avec texte simple
    test_cv_text = """
JEAN DUPONT
Développeur Full-Stack Senior

Email: jean.dupont@email.com
Tel: +33 6 12 34 56 78

EXPÉRIENCE PROFESSIONNELLE
• Senior Developer - TechCorp (2021-2025)
  - Développement d'applications web avec Python/Django
  - Gestion d'équipe de 3 développeurs
  
• Full-Stack Developer - StartupXYZ (2019-2021)
  - Création d'API REST
  - Frontend React.js

COMPÉTENCES
• Python, Django, JavaScript, React
• PostgreSQL, AWS, Docker, Git
• 6 ans d'expérience en développement web

FORMATION
• Master Informatique - Université Lyon 1 (2017-2019)
• Licence Informatique - Université Lyon 1 (2014-2017)

LANGUES
• Français: Langue maternelle
• Anglais: Courant (C1)
• Espagnol: Intermédiaire (B1)
"""
    
    try:
        print("[RUNNING] Debut de l'analyse du CV test...")
        result = service.analyze_cv_with_ai(test_cv_text.strip())
        print("[OK] Analyse terminee avec succes!")
        
        print(f"  - Nom: {result.first_name} {result.last_name}")
        print(f"  - Titre: {result.headline}")
        print(f"  - Experience: {result.years_experience} ans")
        print(f"  - Competences principales: {', '.join(result.skills_primary[:3])}")
        print(f"  - Score global: {result.fit_score_overall}/100")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'analyse: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 60)
    success = test_analysis_service()
    print("=" * 60)
    print(f"Resultat: {'SUCCES' if success else 'ECHEC'}")