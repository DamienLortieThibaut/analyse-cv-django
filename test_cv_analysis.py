#!/usr/bin/env python3
"""
Script pour tester l'analyse CV avec Claude
Usage: python test_cv_analysis.py
"""

import os
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from candidatures.services import CVAnalysisService

def test_claude_analysis():
    """Test de l'analyse CV avec Claude"""
    
    # Votre CV réel (remplacez par votre contenu)
    cv_text = """
KILIAN TROUET
Développeur Full-Stack Senior
kilian.trouet@gmail.com | +33 6 12 34 56 78 | Paris, France
LinkedIn: linkedin.com/in/kilian-trouet | GitHub: github.com/ktrouet

PROFIL PROFESSIONNEL
Développeur Full-Stack avec 6 années d'expérience en développement d'applications web modernes.
Expertise en Python/Django, JavaScript/React et architecture cloud AWS.
Passionné par les technologies émergentes et l'amélioration continue des processus de développement.

EXPÉRIENCE PROFESSIONNELLE

Senior Full-Stack Developer | TechCorp | Paris | 2021 - Présent
• Développement d'une plateforme SaaS servant 50,000+ utilisateurs actifs
• Architecture et implémentation d'APIs RESTful avec Django REST Framework
• Développement frontend avec React/TypeScript et state management Redux
• Mise en place de l'infrastructure CI/CD avec Docker, Jenkins et AWS
• Encadrement technique de 3 développeurs junior
• Amélioration des performances de 40% via optimisation des requêtes SQL

Full-Stack Developer | StartupXYZ | Paris | 2019 - 2021
• Développement from scratch d'une application e-commerce B2B
• Stack technique: Django, PostgreSQL, React, Redis
• Intégration de solutions de paiement (Stripe, PayPal)
• Développement d'un système de recommandation ML avec scikit-learn
• Participation active aux décisions d'architecture technique

Développeur Web Junior | WebAgency | Lyon | 2018 - 2019
• Développement de sites web corporate avec Django et WordPress
• Intégration de maquettes responsive (HTML/CSS/JavaScript)
• Maintenance et évolution d'applications existantes
• Formation aux bonnes pratiques de développement

FORMATION
Master 2 en Informatique, spécialité Développement Web
Université Claude Bernard Lyon 1 | 2016 - 2018
• Projet de fin d'études: Application web de gestion de projets collaboratifs

Licence Informatique
Université Claude Bernard Lyon 1 | 2013 - 2016

COMPÉTENCES TECHNIQUES
Langages: Python, JavaScript/TypeScript, SQL, HTML/CSS
Frameworks Backend: Django, Django REST Framework, FastAPI, Flask  
Frameworks Frontend: React, Vue.js, Angular (bases)
Bases de données: PostgreSQL, MySQL, MongoDB, Redis
Cloud & DevOps: AWS (EC2, RDS, S3), Docker, Jenkins, GitHub Actions
Outils: Git, VS Code, Postman, Figma, Jira

LANGUES
Français: Langue maternelle
Anglais: Courant (C1) - TOEIC 890/990
Espagnol: Intermédiaire (B1)

PROJETS PERSONNELS
• OpenSourceTracker: Application de suivi de contributions open source (Django + React)
• CryptoPortfolio: Dashboard de suivi de portefeuille crypto (Python + APIs)
• PersonalBlog: Blog technique avec système CMS custom (Django)

CERTIFICATIONS
• AWS Certified Developer Associate (2023)
• Scrum Master Certified (2022)
    """
    
    print("Test d'analyse CV avec Claude API")
    print("=" * 50)
    
    try:
        service = CVAnalysisService()
        print("Envoi du CV a Claude...")
        
        # Cette ligne va consommer des crédits Claude
        analysis_result = service.analyze_cv_with_ai(cv_text)
        
        print("Analyse terminee!")
        print("=" * 50)
        print(f"Headline: {analysis_result.headline}")
        print(f"Experience: {analysis_result.years_experience} ans")
        print(f"Formation: {analysis_result.education_highest}")
        print(f"Competences principales: {analysis_result.skills_primary}")
        print(f"Competences secondaires: {analysis_result.skills_secondary}")
        print(f"Langues: {analysis_result.languages}")
        print(f"Localisations: {analysis_result.locations_preferred}")
        print(f"Salaire min/max: {analysis_result.salary_expectation_min}/{analysis_result.salary_expectation_max}")
        print(f"Disponibilite: {analysis_result.availability_date}")
        print(f"Autorisation: {analysis_result.work_authorization}")
        print(f"Score global: {analysis_result.fit_score_overall}/100")
        print(f"Scores detailles: {analysis_result.fit_scores}")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_claude_analysis()
    if success:
        print("\nLe test a reussi! Claude a bien analyse le CV.")
    else:
        print("\nLe test a echoue. Verifiez votre configuration.")