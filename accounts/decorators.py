from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(*allowed_roles):
    """
    Décorateur pour restreindre l'accès selon les rôles
    Usage: @role_required('admin', 'recruteur')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request, 
                    f"Accès refusé. Cette section est réservée aux {', '.join(allowed_roles)}."
                )
                return redirect('accounts:dashboard')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Décorateur pour restreindre l'accès aux admins uniquement
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Accès refusé. Cette section est réservée aux administrateurs.")
            return redirect('accounts:dashboard')
    return _wrapped_view


def recruteur_or_admin_required(view_func):
    """
    Décorateur pour restreindre l'accès aux recruteurs et admins
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['recruteur', 'admin']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Accès refusé. Cette section est réservée aux recruteurs et administrateurs.")
            return redirect('accounts:dashboard')
    return _wrapped_view


def candidat_only(view_func):
    """
    Décorateur pour restreindre l'accès aux candidats uniquement
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'candidat':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Cette section est réservée aux candidats.")
            return redirect('accounts:dashboard')
    return _wrapped_view


# Mixins pour les vues basées sur les classes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin pour restreindre l'accès selon les rôles dans les vues basées sur les classes
    """
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.role not in self.allowed_roles:
            messages.error(
                request, 
                f"Accès refusé. Cette section est réservée aux {', '.join(self.allowed_roles)}."
            )
            return redirect('accounts:dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    """
    Mixin pour restreindre l'accès aux admins uniquement
    """
    allowed_roles = ['admin']


class RecruteurOrAdminRequiredMixin(RoleRequiredMixin):
    """
    Mixin pour restreindre l'accès aux recruteurs et admins
    """
    allowed_roles = ['recruteur', 'admin']


class CandidatOnlyMixin(RoleRequiredMixin):
    """
    Mixin pour restreindre l'accès aux candidats uniquement
    """
    allowed_roles = ['candidat']
