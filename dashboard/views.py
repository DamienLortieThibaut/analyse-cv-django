from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def list_candidatures(request):
    return render(request, 'list.html')
