from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import CustomUser, ProfilRecruteur, ProfilCandidat


class CustomUserCreationForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': 'votre@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': 'Nom'
        })
    )
    role = forms.ChoiceField(
        choices=[
            ('candidat', 'Candidat'),
            ('recruteur', 'Recruteur'),
        ], 
        initial='candidat',
        label='Rôle',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition'
        })
    )
    telephone = forms.CharField(
        max_length=15,
        required=False,
        label='Téléphone',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': '06 12 34 56 78'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'telephone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': 'Confirmer le mot de passe'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé qui utilise l'email"""
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': 'Votre adresse email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
            'placeholder': 'Votre mot de passe'
        })
    )


class UserUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil utilisateur"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style pour tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition'
            })
        
        # Placeholders spécifiques
        self.fields['first_name'].widget.attrs['placeholder'] = 'Prénom'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Nom'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['telephone'].widget.attrs['placeholder'] = 'Téléphone'
        
        # Labels français
        self.fields['first_name'].label = 'Prénom'
        self.fields['last_name'].label = 'Nom'
        self.fields['email'].label = 'Email'
        self.fields['telephone'].label = 'Téléphone'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email


class ProfilRecruteurForm(forms.ModelForm):
    """Formulaire pour le profil recruteur"""
    
    class Meta:
        model = ProfilRecruteur
        fields = ['entreprise', 'poste', 'secteur_activite', 'site_web']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style pour tous les champs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
                    'rows': 4
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition'
                })
        
        # Placeholders et labels
        self.fields['entreprise'].widget.attrs['placeholder'] = 'Nom de l\'entreprise'
        self.fields['poste'].widget.attrs['placeholder'] = 'Votre poste'
        self.fields['secteur_activite'].widget.attrs['placeholder'] = 'Secteur d\'activité'
        self.fields['site_web'].widget.attrs['placeholder'] = 'https://www.exemple.com'
        
        # Labels français
        self.fields['entreprise'].label = 'Entreprise'
        self.fields['poste'].label = 'Poste'
        self.fields['secteur_activite'].label = 'Secteur d\'activité'
        self.fields['site_web'].label = 'Site web'


class ProfilCandidatForm(forms.ModelForm):
    """Formulaire pour le profil candidat"""
    
    class Meta:
        model = ProfilCandidat
        fields = ['date_naissance', 'adresse', 'ville', 'code_postal', 'pays', 
                 'linkedin', 'github', 'portfolio']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style pour tous les champs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
                    'rows': 4
                })
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition',
                    'type': 'date'
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition'
                })
        
        # Placeholders et labels
        self.fields['adresse'].widget.attrs['placeholder'] = 'Votre adresse complète'
        self.fields['ville'].widget.attrs['placeholder'] = 'Votre ville'
        self.fields['code_postal'].widget.attrs['placeholder'] = 'Code postal'
        self.fields['pays'].widget.attrs['placeholder'] = 'Pays'
        self.fields['linkedin'].widget.attrs['placeholder'] = 'https://linkedin.com/in/votre-profil'
        self.fields['github'].widget.attrs['placeholder'] = 'https://github.com/votre-username'
        self.fields['portfolio'].widget.attrs['placeholder'] = 'https://votre-portfolio.com'
        
        # Labels français
        self.fields['date_naissance'].label = 'Date de naissance'
        self.fields['adresse'].label = 'Adresse'
        self.fields['ville'].label = 'Ville'
        self.fields['code_postal'].label = 'Code postal'
        self.fields['pays'].label = 'Pays'
        self.fields['linkedin'].label = 'Profil LinkedIn'
        self.fields['github'].label = 'Profil GitHub'
        self.fields['portfolio'].label = 'Portfolio'


class ChangePasswordForm(PasswordChangeForm):
    """Formulaire personnalisé pour changer le mot de passe"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style pour tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-800 bg-slate-900/60 focus:border-violet-500 focus:outline-none transition'
            })
        
        # Placeholders et labels français
        self.fields['old_password'].widget.attrs['placeholder'] = 'Mot de passe actuel'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Nouveau mot de passe'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirmer le nouveau mot de passe'
        
        self.fields['old_password'].label = 'Mot de passe actuel'
        self.fields['new_password1'].label = 'Nouveau mot de passe'
        self.fields['new_password2'].label = 'Confirmer le nouveau mot de passe'
