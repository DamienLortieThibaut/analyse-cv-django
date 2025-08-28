from django.shortcuts import render

def home(request):
    return render(request, 'dashboard/home.html')

def list_candidatures(request):
    return render(request, 'dashboard/list.html')
