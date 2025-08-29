from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import recruteur_or_admin_required

@login_required
def home(request):
    return render(request, 'dashboard/home.html')

@recruteur_or_admin_required
def list_candidatures(request):
    return render(request, 'dashboard/list.html')
