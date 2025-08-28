from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser, ProfilRecruteur, ProfilCandidat


class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre adresse email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom'
        })
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        initial='candidat',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    telephone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+33123456789'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les widgets des mots de passe
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cette adresse email existe déjà.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.telephone = self.cleaned_data.get('telephone', '')
        
        if commit:
            user.save()
            
            # Créer le profil correspondant selon le rôle
            if user.role == 'recruteur':
                ProfilRecruteur.objects.create(user=user, entreprise="", poste="")
            elif user.role == 'candidat':
                ProfilCandidat.objects.create(user=user)
        
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé qui utilise l'email
    """
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre adresse email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe'
        })
    )
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = "Email"


class ProfilRecruteurForm(forms.ModelForm):
    """
    Formulaire pour le profil recruteur
    """
    class Meta:
        model = ProfilRecruteur
        fields = ['entreprise', 'poste', 'secteur_activite', 'site_web']
        widgets = {
            'entreprise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de votre entreprise'
            }),
            'poste': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre poste'
            }),
            'secteur_activite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Secteur d\'activité'
            }),
            'site_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.entreprise.com'
            }),
        }


class ProfilCandidatForm(forms.ModelForm):
    """
    Formulaire pour le profil candidat
    """
    class Meta:
        model = ProfilCandidat
        fields = [
            'date_naissance', 'adresse', 'ville', 'code_postal', 
            'pays', 'linkedin', 'github', 'portfolio'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Votre adresse complète'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre ville'
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code postal'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pays'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/votre-profil'
            }),
            'github': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/votre-username'
            }),
            'portfolio': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://votre-portfolio.com'
            }),
        }


class UserUpdateForm(forms.ModelForm):
    """
    Formulaire pour modifier les informations de base de l'utilisateur
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+33123456789'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Un autre compte utilise déjà cette adresse email.")
        return email


class ChangePasswordForm(forms.Form):
    """
    Formulaire pour changer le mot de passe
    """
    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        }),
        validators=[validate_password]
    )
    new_password2 = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("L'ancien mot de passe est incorrect.")
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        
        return cleaned_data
    
    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user
