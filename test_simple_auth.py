#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

def test_auth():
    User = get_user_model()
    
    print("=== Test Auth Admin ===")
    
    # Vérifier utilisateur
    try:
        user = User.objects.get(email='admin@test.com')
        print(f"User trouvé: {user.email}")
        print(f"Is superuser: {user.is_superuser}")
        print(f"Is staff: {user.is_staff}")
        print(f"Is active: {user.is_active}")
    except:
        print("User NOT found")
        return
    
    # Test password
    print(f"Password check: {user.check_password('admin123')}")
    
    # Test auth avec email
    auth1 = authenticate(username='admin@test.com', password='admin123')
    print(f"Auth with email: {auth1 is not None}")
    
    # Test auth avec username  
    auth2 = authenticate(username='admin', password='admin123')
    print(f"Auth with username: {auth2 is not None}")
    
    # Reset password pour être sûr
    user.set_password('admin123')
    user.save()
    print("Password reset to 'admin123'")
    
    # Test après reset
    auth3 = authenticate(username='admin@test.com', password='admin123')
    print(f"Auth after reset: {auth3 is not None}")

if __name__ == "__main__":
    test_auth()