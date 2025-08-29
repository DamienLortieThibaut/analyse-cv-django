from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.decorators import recruteur_or_admin_required
from candidatures.models import Candidature, StatusChoices

@login_required
def home(request):
    # Filtrer par email si présent dans l'URL
    email_filter = request.GET.get('email')
    queryset = Candidature.objects.all()
    
    if email_filter:
        queryset = queryset.filter(email=email_filter)
    
    # Calculer les KPIs
    total_candidatures = queryset.count()
    en_revue = queryset.filter(status__in=['screening', 'manager_review', 'tech_test']).count()
    preselection = queryset.filter(status__in=['interview_1', 'offer']).count()
    embauches = queryset.filter(status='hired').count()
    
    # Taux de conversion (embauches / total)
    taux_conversion = (embauches / total_candidatures * 100) if total_candidatures > 0 else 0
    
    # Score moyen
    score_moyen = queryset.aggregate(avg_score=Avg('fit_score_overall'))['avg_score'] or 0
    
    # Variations (simulées pour l'exemple - vous pouvez calculer par rapport à la période précédente)
    total_change = "+8"  # À calculer avec une vraie logique temporelle
    revue_change = "-2"
    preselection_change = "+3"
    conversion_change = "+2.0 pts"
    score_change = "+1.4"
    
    context = {
        'email_filter': email_filter,
        'kpis': {
            'total_candidatures': {'value': total_candidatures, 'change': total_change, 'positive': True},
            'en_revue': {'value': en_revue, 'change': revue_change, 'positive': False},
            'preselection': {'value': preselection, 'change': preselection_change, 'positive': True},
            'taux_conversion': {'value': f"{taux_conversion:.1f}%", 'change': conversion_change, 'positive': True},
            'score_moyen': {'value': f"{score_moyen:.1f}", 'change': score_change, 'positive': True},
        }
    }
    return render(request, 'dashboard/home.html', context)

@recruteur_or_admin_required
def list_candidatures(request):
    return render(request, 'dashboard/list.html')

@login_required
def dashboard_data_api(request):
    """API pour fournir les données des graphiques en temps réel"""
    
    # Filtrer par email si présent dans l'URL
    email_filter = request.GET.get('email')
    queryset = Candidature.objects.all()
    
    if email_filter:
        queryset = queryset.filter(email=email_filter)
    
    # Répartition par statut
    status_data = list(queryset.values('status').annotate(count=Count('id')))
    status_labels = []
    status_values = []
    
    status_mapping = {
        'submitted': 'Soumise',
        'screening': 'En sélection',
        'manager_review': 'Revue managériale', 
        'tech_test': 'Test technique',
        'interview_1': 'Entretien',
        'offer': 'Offre émise',
        'hired': 'Embauché(e)',
        'rejected': 'Rejetée'
    }
    
    for item in status_data:
        status_labels.append(status_mapping.get(item['status'], item['status']))
        status_values.append(item['count'])
    
    # Top des postes (basé sur position_applied ou headline)
    postes_data = list(queryset.exclude(position_applied='')
                      .values('position_applied')
                      .annotate(count=Count('id'))
                      .order_by('-count')[:6])
    
    if not postes_data:  # Fallback sur headline si position_applied est vide
        postes_data = list(queryset.exclude(headline='')
                          .values('headline')
                          .annotate(count=Count('id'))
                          .order_by('-count')[:6])
        postes_labels = [item['headline'][:20] + '...' if len(item['headline']) > 20 else item['headline'] for item in postes_data]
    else:
        postes_labels = [item['position_applied'] for item in postes_data]
    
    postes_values = [item['count'] for item in postes_data]
    
    # Tendance hebdomadaire (dernières 8 semaines)
    today = timezone.now().date()
    weeks_data = []
    week_labels = []
    
    for i in range(7, -1, -1):
        week_start = today - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        
        count = queryset.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).count()
        
        weeks_data.append(count)
        week_labels.append(week_start.strftime("%m-%d"))
    
    return JsonResponse({
        'status_chart': {
            'labels': status_labels,
            'values': status_values
        },
        'postes_chart': {
            'labels': postes_labels,
            'values': postes_values
        },
        'tendance_chart': {
            'labels': week_labels,
            'values': weeks_data
        }
    })
