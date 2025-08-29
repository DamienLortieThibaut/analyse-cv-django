from django.contrib import admin
from .models import Candidature


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'headline', 'fit_score_overall', 'status', 'created_at')
    list_filter = ('status', 'work_authorization', 'priority', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'headline')
    readonly_fields = ('id', 'created_at', 'updated_at', 'analyzed_at')
    
    fieldsets = (
        ('Documents & Identité', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'resume', 'cv_url')
        }),
        ('Profil professionnel', {
            'fields': ('headline', 'summary', 'years_experience', 'education_highest')
        }),
        ('Expériences professionnelles', {
            'fields': ('experiences',),
            'classes': ('collapse',)
        }),
        ('Formation & Éducation', {
            'fields': ('education',),
            'classes': ('collapse',)
        }),
        ('Compétences & Intérêts', {
            'fields': ('skills_primary', 'skills_secondary', 'languages', 'interests'),
            'classes': ('collapse',)
        }),
        ('Préférences', {
            'fields': ('locations_preferred', 'salary_expectation_min', 'salary_expectation_max', 
                      'availability_date', 'work_authorization'),
            'classes': ('collapse',)
        }),
        ('Évaluation', {
            'fields': ('fit_score_overall', 'fit_scores', 'model_version')
        }),
        ('Suivi', {
            'fields': ('status', 'status_reason', 'priority', 'position_applied', 'message')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at', 'analyzed_at'),
            'classes': ('collapse',)
        }),
    )
