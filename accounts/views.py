from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    ProfilRecruteurForm, 
    ProfilCandidatForm,
    UserUpdateForm,
    ChangePasswordForm
)
from .models import CustomUser, ProfilRecruteur, ProfilCandidat


def home(request):
    """
    Page d'accueil
    """
    return render(request, 'accounts/home.html')


class RegisterView(CreateView):
    """
    Vue d'inscription avec JWT
    """
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    
    def form_valid(self, form):
        # Sauvegarder l'utilisateur
        user = form.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        messages.success(self.request, f'Compte créé avec succès ! Bienvenue {user.first_name} !')
        
        # Rediriger vers le dashboard
        response = redirect('accounts:dashboard')
        
        # Stocker les tokens JWT en cookies
        response.set_cookie('access_token', access_token, max_age=3600, httponly=True, secure=False, samesite='Lax')
        response.set_cookie('refresh_token', refresh_token, max_age=604800, httponly=True, secure=False, samesite='Lax')
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inscription'
        return context


def login_view(request):
    """
    Vue de connexion
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Le champ s'appelle username mais contient l'email
            password = form.cleaned_data.get('password')
            
            # Authentifier avec l'email
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Générer les tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                
                messages.success(request, f'Bienvenue, {user.first_name} !')
                
                # Rediriger vers le dashboard
                next_url = request.GET.get('next')
                if next_url:
                    response = redirect(next_url)
                else:
                    response = redirect('accounts:dashboard')
                
                # Stocker les tokens JWT en cookies
                response.set_cookie('access_token', access_token, max_age=3600, httponly=True, secure=False, samesite='Lax')
                response.set_cookie('refresh_token', refresh_token, max_age=604800, httponly=True, secure=False, samesite='Lax')
                
                return response
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Connexion'
    })


def logout_view(request):
    """
    Vue de déconnexion JWT
    """
    # Tenter de blacklister le refresh token s'il existe
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass  # Token invalide ou déjà blacklisté
    
    # Créer la réponse de redirection
    response = redirect('accounts:home')
    
    # Supprimer les cookies JWT
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return response


@login_required
def dashboard(request):
    """
    Tableau de bord personnalisé selon le rôle
    """
    user = request.user
    context = {
        'title': 'Tableau de bord',
        'user': user
    }
    
    # Ajouter les données spécifiques selon le rôle
    if user.is_recruteur():
        try:
            context['profil_recruteur'] = user.profil_recruteur
        except ProfilRecruteur.DoesNotExist:
            ProfilRecruteur.objects.create(user=user, entreprise="", poste="")
            context['profil_recruteur'] = user.profil_recruteur
        
        # Statistiques pour les recruteurs
        context['stats'] = {
            'candidatures_total': 0,  # À implémenter plus tard
            'candidatures_mois': 0,   # À implémenter plus tard
        }
        
    elif user.is_candidat():
        try:
            context['profil_candidat'] = user.profil_candidat
        except ProfilCandidat.DoesNotExist:
            ProfilCandidat.objects.create(user=user)
            context['profil_candidat'] = user.profil_candidat
        
        # Statistiques pour les candidats
        context['stats'] = {
            'candidatures_envoyees': 0,  # À implémenter plus tard
            'reponses_recues': 0,         # À implémenter plus tard
        }
    
    elif user.is_admin():
        # Statistiques pour les admins
        context['stats'] = {
            'total_users': CustomUser.objects.count(),
            'total_candidats': CustomUser.objects.filter(role='candidat').count(),
            'total_recruteurs': CustomUser.objects.filter(role='recruteur').count(),
            'users_actifs': CustomUser.objects.filter(est_actif=True).count(),
        }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    """
    Vue du profil utilisateur
    """
    user = request.user
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        
        # Formulaire spécifique selon le rôle
        if user.is_recruteur():
            try:
                profil = user.profil_recruteur
            except ProfilRecruteur.DoesNotExist:
                profil = ProfilRecruteur.objects.create(user=user, entreprise="", poste="")
            
            profil_form = ProfilRecruteurForm(request.POST, instance=profil)
            
        elif user.is_candidat():
            try:
                profil = user.profil_candidat
            except ProfilCandidat.DoesNotExist:
                profil = ProfilCandidat.objects.create(user=user)
            
            profil_form = ProfilCandidatForm(request.POST, instance=profil)
        else:
            profil_form = None
        
        # Validation et sauvegarde
        if user_form.is_valid() and (profil_form is None or profil_form.is_valid()):
            user_form.save()
            if profil_form:
                profil_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    
    else:
        user_form = UserUpdateForm(instance=user)
        
        if user.is_recruteur():
            try:
                profil = user.profil_recruteur
            except ProfilRecruteur.DoesNotExist:
                profil = ProfilRecruteur.objects.create(user=user, entreprise="", poste="")
            profil_form = ProfilRecruteurForm(instance=profil)
            
        elif user.is_candidat():
            try:
                profil = user.profil_candidat
            except ProfilCandidat.DoesNotExist:
                profil = ProfilCandidat.objects.create(user=user)
            profil_form = ProfilCandidatForm(instance=profil)
        else:
            profil_form = None
    
    return render(request, 'accounts/profile.html', {
        'title': 'Mon Profil',
        'user_form': user_form,
        'profil_form': profil_form,
        'user': user
    })


@login_required
def change_password_view(request):
    """
    Vue pour changer le mot de passe
    """
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre mot de passe a été modifié avec succès.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, 'accounts/change_password.html', {
        'title': 'Changer le mot de passe',
        'form': form
    })


class UserListView(LoginRequiredMixin, ListView):
    """
    Liste des utilisateurs (réservée aux admins)
    """
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'Accès refusé. Vous devez être administrateur.')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return CustomUser.objects.all().order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestion des utilisateurs'
        context['total_users'] = CustomUser.objects.count()
        context['active_users'] = CustomUser.objects.filter(est_actif=True).count()
        return context


@login_required
def toggle_user_status(request, user_id):
    """
    Activer/désactiver un utilisateur (réservé aux admins)
    """
    if not request.user.is_admin():
        messages.error(request, 'Accès refusé.')
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    
    if user == request.user:
        messages.error(request, 'Vous ne pouvez pas désactiver votre propre compte.')
        return redirect('accounts:user_list')
    
    user.est_actif = not user.est_actif
    user.save()
    
    status = "activé" if user.est_actif else "désactivé"
    messages.success(request, f'L\'utilisateur {user.email} a été {status}.')
    
    return redirect('accounts:user_list')


@login_required
def admin_users(request):
    """
    Vue pour la gestion des utilisateurs (réservée aux administrateurs)
    """
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux administrateurs.")
        return redirect('accounts:dashboard')
    
    # Récupérer tous les utilisateurs
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Statistiques
    stats = {
        'total_users': CustomUser.objects.count(),
        'admins': CustomUser.objects.filter(role='admin').count(),
        'recruteurs': CustomUser.objects.filter(role='recruteur').count(),
        'candidats': CustomUser.objects.filter(role='candidat').count(),
    }
    
    context = {
        'users': users,
        'stats': stats,
    }
    
    return render(request, 'accounts/admin_users.html', context)