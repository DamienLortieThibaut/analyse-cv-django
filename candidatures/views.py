from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta

# Données fictives pour les candidatures
CANDIDATURES_FICTIVES = [
    {
        'pk': 1,
        'nom': 'Alice Durand',
        'poste': 'data_analyst',
        'statut': 'preselection',
        'score': 88,
        'date_creation': datetime.now() - timedelta(days=2),
        'date_modification': datetime.now() - timedelta(hours=3),
    },
    {
        'pk': 2,
        'nom': 'Marc Lefebvre',
        'poste': 'dev_front',
        'statut': 'en_revue',
        'score': 72,
        'date_creation': datetime.now() - timedelta(days=5),
        'date_modification': datetime.now() - timedelta(days=1),
    },
    {
        'pk': 3,
        'nom': 'Sophie Martin',
        'poste': 'ux_designer',
        'statut': 'embauchee',
        'score': 95,
        'date_creation': datetime.now() - timedelta(days=15),
        'date_modification': datetime.now() - timedelta(days=7),
    },
    {
        'pk': 4,
        'nom': 'Thomas Bernard',
        'poste': 'qa_engineer',
        'statut': 'soumise',
        'score': 65,
        'date_creation': datetime.now() - timedelta(days=1),
        'date_modification': datetime.now() - timedelta(hours=12),
    },
    {
        'pk': 5,
        'nom': 'Laura Rodriguez',
        'poste': 'product_manager',
        'statut': 'rejetee',
        'score': 45,
        'date_creation': datetime.now() - timedelta(days=8),
        'date_modification': datetime.now() - timedelta(days=3),
    },
    {
        'pk': 6,
        'nom': 'Kevin Moreau',
        'poste': 'dev_front',
        'statut': 'en_revue',
        'score': 78,
        'date_creation': datetime.now() - timedelta(days=4),
        'date_modification': datetime.now() - timedelta(hours=6),
    },
    {
        'pk': 7,
        'nom': 'Emma Leroy',
        'poste': 'data_analyst',
        'statut': 'preselection',
        'score': 91,
        'date_creation': datetime.now() - timedelta(days=6),
        'date_modification': datetime.now() - timedelta(days=2),
    },
    {
        'pk': 8,
        'nom': 'Nicolas Petit',
        'poste': 'qa_engineer',
        'statut': 'soumise',
        'score': 69,
        'date_creation': datetime.now() - timedelta(hours=8),
        'date_modification': datetime.now() - timedelta(hours=8),
    }
]

# Mapping des postes
POSTES_CHOICES = {
    'data_analyst': 'Data Analyst',
    'dev_front': 'Développeur Front',
    'qa_engineer': 'QA Engineer',
    'product_manager': 'Product Manager',
    'ux_designer': 'UX Designer',
}

# Mapping des statuts
STATUTS_CHOICES = {
    'soumise': 'Soumise',
    'en_revue': 'En revue',
    'preselection': 'Présélection',
    'rejetee': 'Rejetée',
    'embauchee': 'Embauché(e)',
}

class CandidatureFictive:
    """Classe pour simuler un objet candidature"""
    def __init__(self, data):
        self.pk = data['pk']
        self.nom = data['nom']
        self.poste = data['poste']
        self.statut = data['statut']
        self.score = data['score']
        self.date_creation = data['date_creation']
        self.date_modification = data['date_modification']
    
    def get_poste_display(self):
        return POSTES_CHOICES.get(self.poste, self.poste)
    
    def get_statut_display(self):
        return STATUTS_CHOICES.get(self.statut, self.statut)

def index(request):
    """Page d'accueil de l'app candidatures"""
    return render(request, 'index.html')

def list_candidatures(request):
    """Liste des candidatures avec filtres"""
    candidatures_data = CANDIDATURES_FICTIVES.copy()
    
    # Filtres
    poste = request.GET.get('poste')
    statut = request.GET.get('statut')
    score_min = request.GET.get('score_min')
    search = request.GET.get('search')
    
    if poste:
        candidatures_data = [c for c in candidatures_data if c['poste'] == poste]
    
    if statut:
        candidatures_data = [c for c in candidatures_data if c['statut'] == statut]
    
    if score_min:
        try:
            score_min_int = int(score_min)
            candidatures_data = [c for c in candidatures_data if c['score'] >= score_min_int]
        except ValueError:
            pass
    
    if search:
        candidatures_data = [c for c in candidatures_data if search.lower() in c['nom'].lower()]
    
    # Convertir en objets CandidatureFictive
    candidatures = [CandidatureFictive(data) for data in candidatures_data]
    
    context = {
        'candidatures': candidatures,
    }
    return render(request, 'list.html', context)

def detail_candidature(request, pk):
    """Détail d'une candidature"""
    candidature_data = next((c for c in CANDIDATURES_FICTIVES if c['pk'] == pk), None)
    
    if not candidature_data:
        # Retourner une 404 ou rediriger
        candidature = None
    else:
        candidature = CandidatureFictive(candidature_data)
    
    context = {
        'candidature': candidature,
    }
    return render(request, 'detail.html', context)

def delete_candidature(request, pk):
    """Suppression d'une candidature"""
    candidature_data = next((c for c in CANDIDATURES_FICTIVES if c['pk'] == pk), None)
    
    if not candidature_data:
        candidature = None
    else:
        candidature = CandidatureFictive(candidature_data)
    
    if request.method == 'POST':
        # Simuler la suppression
        messages.success(request, f'La candidature de {candidature.nom} a été supprimée avec succès.')
        from django.shortcuts import redirect
        return redirect('candidatures:list')
    
    context = {
        'candidature': candidature,
    }
    return render(request, 'delete_confirm.html', context)
