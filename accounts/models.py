from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé avec différents rôles
    """
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
    ]
    
    # Champs personnalisés
    email = models.EmailField(unique=True, verbose_name="Email")
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='candidat',
        verbose_name="Rôle"
    )
    telephone = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
        )],
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    est_actif = models.BooleanField(default=True, verbose_name="Compte actif")
    
    # Utilisation de l'email comme identifiant de connexion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        db_table = 'auth_custom_user'
    
    def __str__(self):
        return f"{self.email} - {self.get_role_display()}"
    
    @property
    def nom_complet(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_admin(self):
        """Vérifie si l'utilisateur est un administrateur"""
        return self.role == 'admin'
    
    def is_recruteur(self):
        """Vérifie si l'utilisateur est un recruteur"""
        return self.role == 'recruteur'
    
    def is_candidat(self):
        """Vérifie si l'utilisateur est un candidat"""
        return self.role == 'candidat'


class ProfilRecruteur(models.Model):
    """
    Profil étendu pour les recruteurs
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_recruteur')
    entreprise = models.CharField(max_length=255, verbose_name="Entreprise")
    poste = models.CharField(max_length=255, verbose_name="Poste")
    secteur_activite = models.CharField(max_length=255, blank=True, null=True, verbose_name="Secteur d'activité")
    site_web = models.URLField(blank=True, null=True, verbose_name="Site web")
    
    class Meta:
        verbose_name = "Profil Recruteur"
        verbose_name_plural = "Profils Recruteurs"
    
    def __str__(self):
        return f"{self.user.nom_complet} - {self.entreprise}"


class ProfilCandidat(models.Model):
    """
    Profil étendu pour les candidats
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_candidat')
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    code_postal = models.CharField(max_length=10, blank=True, null=True, verbose_name="Code postal")
    pays = models.CharField(max_length=100, default="France", verbose_name="Pays")
    linkedin = models.URLField(blank=True, null=True, verbose_name="Profil LinkedIn")
    github = models.URLField(blank=True, null=True, verbose_name="Profil GitHub")
    portfolio = models.URLField(blank=True, null=True, verbose_name="Portfolio")
    
    class Meta:
        verbose_name = "Profil Candidat"
        verbose_name_plural = "Profils Candidats"
    
    def __str__(self):
        return f"{self.user.nom_complet} - Candidat"
