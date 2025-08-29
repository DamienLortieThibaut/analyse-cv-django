#!/usr/bin/env python
"""
Test extraction nom depuis fichier
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from candidatures.services import CVAnalysisService

def test_filename_extraction():
    print("=== Test Extraction Nom depuis Fichier ===")
    
    service = CVAnalysisService()
    
    # Tester avec différents noms de fichiers
    test_files = [
        "Damien_LORTIE--THIBAUT_CV.pdf",
        "kilian_cashflow_CV.pdf", 
        "Marie-Dupont-CV.pdf",
        "jean.martin.resume.pdf",
        "cv_pierre_bernard.pdf"
    ]
    
    for filename in test_files:
        print(f"\nTest avec: {filename}")
        try:
            # Utiliser mode factice avec nom de fichier
            result = service._mock_analysis_response("CV test", filename)
            print(f"  Nom detecte: {result.first_name} {result.last_name}")
            print(f"  Titre: {result.headline}")
        except Exception as e:
            print(f"  Erreur: {str(e)}")

if __name__ == "__main__":
    test_filename_extraction()