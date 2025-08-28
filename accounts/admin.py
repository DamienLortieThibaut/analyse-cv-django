from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, ProfilRecruteur, ProfilCandidat


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined', 'role_badge')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'telephone')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'telephone')}),
        ('Rôle et permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'telephone', 'role', 'password1', 'password2'),
        }),
    )
    
    def role_badge(self, obj):
        colors = {
            'admin': '#dc3545',      # Rouge
            'recruteur': '#fd7e14',  # Orange
            'candidat': '#198754'    # Vert
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Rôle'


@admin.register(ProfilRecruteur)
class ProfilRecruteurAdmin(admin.ModelAdmin):
    list_display = ('user', 'entreprise', 'secteur_activite')
    list_filter = ('secteur_activite',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'entreprise', 'secteur_activite')
    
    fieldsets = (
        ('Utilisateur', {'fields': ('user',)}),
        ('Informations entreprise', {'fields': ('entreprise', 'secteur_activite', 'site_web', 'description_entreprise')}),
        ('Informations contact', {'fields': ('adresse', 'ville', 'code_postal', 'pays')}),
    )


@admin.register(ProfilCandidat)
class ProfilCandidatAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    
    fieldsets = (
        ('Utilisateur', {'fields': ('user',)}),
        ('Documents', {'fields': ('cv', 'lettre_motivation')}),
    )
