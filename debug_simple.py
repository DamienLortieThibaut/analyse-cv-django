#!/usr/bin/env python
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

def debug_analyze_page():
    print("Debug Page Analyze")
    
    client = Client()
    
    # Creer session
    session = SessionStore()
    session['pending_candidature'] = {
        'email': 'test@example.com',
        'cv_file_path': 'cvs/test.pdf',
        'cv_file_url': 'http://test.com/test.pdf',
        'uploaded_at': '2024-01-01T00:00:00Z'
    }
    session.save()
    
    client.cookies['sessionid'] = session.session_key
    response = client.get('/candidatures/analyze/')
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Recherches
        has_api_url = 'api/analyze' in content
        has_js = 'Starting analysis' in content
        has_fetch = 'fetch(' in content
        
        print(f"API URL presente: {has_api_url}")
        print(f"JavaScript present: {has_js}")
        print(f"Fetch present: {has_fetch}")
        
        if has_fetch:
            # Extraire la ligne fetch
            lines = content.split('\n')
            for line in lines:
                if 'fetch(' in line and 'api' in line:
                    print(f"Ligne fetch: {line.strip()}")
                    break

if __name__ == "__main__":
    debug_analyze_page()