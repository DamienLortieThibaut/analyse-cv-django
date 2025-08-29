#!/usr/bin/env python
"""
Script pour créer un utilisateur admin
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnalyseCVProject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    """Créer ou réinitialiser l'admin"""
    
    email = "admin@test.com"
    password = "admin123"
    
    # Supprimer l'admin existant s'il existe
    try:
        existing_user = User.objects.get(email=email)
        existing_user.delete()
        print(f"Utilisateur existant {email} supprimé")
    except User.DoesNotExist:
        pass
    
    # Créer le nouvel admin
    admin_user = User.objects.create_user(
        username="admin",  # Nécessaire même si on utilise email comme LOGIN
        email=email,
        password=password,
        first_name="Admin",
        last_name="System",
        role="admin"
    )
    
    # Lui donner les droits superuser
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    
    print("Utilisateur admin créé avec succès!")
    print(f"Email: {email}")
    print(f"Mot de passe: {password}")
    print("URL admin: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    create_admin()