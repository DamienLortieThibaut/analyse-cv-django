#!/usr/bin/env python
"""
Test de connexion admin
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from django.test import Client

def test_admin_auth():
    """Test d'authentification admin"""
    
    User = get_user_model()
    
    print("=== Test Authentification ===")
    
    # Test 1: Vérifier l'utilisateur
    try:
        user = User.objects.get(email='admin@test.com')
        print(f"✓ Utilisateur trouvé: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  Is superuser: {user.is_superuser}")
        print(f"  Is staff: {user.is_staff}")
        print(f"  Is active: {user.is_active}")
    except User.DoesNotExist:
        print("✗ Utilisateur admin@test.com non trouvé")
        return
    
    # Test 2: Authentification avec email
    print("\n=== Test Auth avec Email ===")
    auth_user = authenticate(username='admin@test.com', password='admin123')
    if auth_user:
        print("✓ Auth avec email réussie")
    else:
        print("✗ Auth avec email échouée")
    
    # Test 3: Authentification avec username
    print("\n=== Test Auth avec Username ===") 
    auth_user2 = authenticate(username='admin', password='admin123')
    if auth_user2:
        print("✓ Auth avec username réussie")
    else:
        print("✗ Auth avec username échouée")
    
    # Test 4: Test login via Django test client
    print("\n=== Test Login Admin Interface ===")
    client = Client()
    
    # Test avec email
    response = client.post('/admin/login/', {
        'username': 'admin@test.com',
        'password': 'admin123'
    })
    print(f"Login avec email: {response.status_code}")
    
    # Test avec username 
    client2 = Client()
    response2 = client2.post('/admin/login/', {
        'username': 'admin',
        'password': 'admin123'
    })
    print(f"Login avec username: {response2.status_code}")
    
    # Test accès admin après login
    if response.status_code in [200, 302]:
        admin_response = client.get('/admin/')
        print(f"Accès admin après login: {admin_response.status_code}")

def test_password():
    """Test si le mot de passe est correct"""
    User = get_user_model()
    
    try:
        user = User.objects.get(email='admin@test.com')
        print(f"\n=== Test Mot de Passe ===")
        print(f"Check password 'admin123': {user.check_password('admin123')}")
        print(f"Check password 'admin': {user.check_password('admin')}")
        
        # Réinitialiser le mot de passe au cas où
        user.set_password('admin123')
        user.save()
        print("Mot de passe réinitialisé à 'admin123'")
        
    except User.DoesNotExist:
        print("Utilisateur non trouvé pour test password")

if __name__ == "__main__":
    test_admin_auth()
    test_password()