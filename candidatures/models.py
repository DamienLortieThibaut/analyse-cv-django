from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


class WorkAuthorizationChoices(models.TextChoices):
    EU = 'EU', 'Autorisation UE'
    VISA = 'Visa', 'Visa requis'
    NO = 'No', 'Aucune autorisation'


class StatusChoices(models.TextChoices):
    SUBMITTED = 'submitted', 'Soumise'
    SCREENING = 'screening', 'En sélection'
    MANAGER_REVIEW = 'manager_review', 'Revue managériale'
    TECH_TEST = 'tech_test', 'Test technique'
    INTERVIEW_1 = 'interview_1', 'Premier entretien'
    OFFER = 'offer', 'Offre émise'
    HIRED = 'hired', 'Embauché'
    REJECTED = 'rejected', 'Rejeté'


class PriorityChoices(models.TextChoices):
    LOW = 'low', 'Basse'
    NORMAL = 'normal', 'Normale'
    HIGH = 'high', 'Haute'


class Candidature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Identité & documents
    resume = models.URLField(max_length=500, help_text="Lien vers le CV")
    cv_url = models.URLField(max_length=500, blank=True, help_text="URL du CV original")
    headline = models.CharField(max_length=255, help_text="Titre accrocheur du profil")
    summary = models.TextField(blank=True, help_text="Résumé complet du CV")
    
    # Informations candidat
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    email = models.EmailField(default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    position_applied = models.CharField(max_length=200, blank=True, default='')
    message = models.TextField(blank=True, default='')
    
    # Expérience & compétences
    years_experience = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        validators=[MinValueValidator(0)],
        help_text="Nombre d'années d'expérience"
    )
    experiences = models.JSONField(
        default=list,
        blank=True,
        help_text="Expériences professionnelles (ex: [{'company': 'TechCorp', 'position': 'Dev Senior', 'duration': '2020-2024', 'description': '...'}])"
    )
    skills_primary = models.JSONField(
        default=list,
        help_text="Compétences principales (liste de strings)"
    )
    skills_secondary = models.JSONField(
        default=list,
        help_text="Compétences secondaires (liste de strings)"
    )
    languages = models.JSONField(
        default=list,
        help_text="Langues parlées avec niveau (ex: [{'fr': 'C2'}, {'en': 'B2'}])"
    )
    education_highest = models.CharField(
        max_length=255,
        help_text="Diplôme le plus élevé"
    )
    education = models.JSONField(
        default=list,
        blank=True,
        help_text="Formations (ex: [{'school': 'Université X', 'degree': 'Master Info', 'duration': '2016-2018'}])"
    )
    interests = models.JSONField(
        default=list,
        blank=True,
        help_text="Centres d'intérêt (liste de strings)"
    )
    
    # Préférences & attentes
    locations_preferred = models.JSONField(
        default=list,
        help_text="Localisations préférées (liste de strings)"
    )
    salary_expectation_min = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Salaire annuel minimum souhaité"
    )
    salary_expectation_max = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Salaire annuel maximum souhaité"
    )
    availability_date = models.DateField(
        null=True, blank=True,
        help_text="Date de disponibilité"
    )
    work_authorization = models.CharField(
        max_length=10,
        choices=WorkAuthorizationChoices.choices,
        default=WorkAuthorizationChoices.EU
    )
    
    # Suivi du recrutement
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.SUBMITTED
    )
    status_reason = models.TextField(
        blank=True,
        help_text="Raison du statut (ex: motif de rejet)"
    )
    priority = models.CharField(
        max_length=10,
        choices=PriorityChoices.choices,
        default=PriorityChoices.NORMAL
    )
    
    # Évaluation & scoring
    fit_score_overall = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score global (0-100)"
    )
    fit_scores = models.JSONField(
        default=dict,
        help_text="Détails par critère (ex: {'skills': 82, 'experience': 75})"
    )
    model_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Version du modèle IA utilisé pour scorer"
    )
    
    # Métadonnées
    analyzed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
    
    def __str__(self):
        return f"{self.headline} - {self.status}"
