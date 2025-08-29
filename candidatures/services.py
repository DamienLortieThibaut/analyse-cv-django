import os
from io import BytesIO
from typing import Dict, Any, Optional
from pathlib import Path
from django.conf import settings
from pdfminer.high_level import extract_text
from pydantic import BaseModel, Field, field_validator
import anthropic
import json
from decimal import Decimal
from datetime import datetime
try:
    from pdf2image import convert_from_bytes
    import pytesseract
    import platform
    
    # Configuration du chemin Tesseract pour Windows
    if platform.system() == "Windows":
        # Chemins courants d'installation de Tesseract sur Windows
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\laragon\bin\tesseract\tesseract.exe",
            r"C:\tools\tesseract\tesseract.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class CVAnalysisResponse(BaseModel):
    """Modèle Pydantic pour valider la réponse d'analyse de CV"""
    
    headline: str = Field(..., max_length=255, description="Titre accrocheur du profil")
    summary: str = Field(..., description="Résumé complet du CV")
    years_experience: float = Field(..., ge=0, description="Années d'expérience")
    experiences: list[Dict[str, str]] = Field(default_factory=list, description="Expériences professionnelles")
    skills_primary: list[str] = Field(..., description="Compétences principales")
    skills_secondary: list[str] = Field(default_factory=list, description="Compétences secondaires")
    languages: list[Dict[str, str]] = Field(default_factory=list, description="Langues avec niveaux")
    education_highest: str = Field(..., max_length=255, description="Diplôme le plus élevé")
    education: list[Dict[str, str]] = Field(default_factory=list, description="Formations détaillées")
    interests: list[str] = Field(default_factory=list, description="Centres d'intérêt")
    locations_preferred: list[str] = Field(default_factory=list, description="Localisations préférées")
    salary_expectation_min: Optional[int] = Field(None, ge=0, description="Salaire minimum")
    salary_expectation_max: Optional[int] = Field(None, ge=0, description="Salaire maximum")
    availability_date: Optional[str] = Field(None, description="Date de disponibilité (YYYY-MM-DD)")
    work_authorization: str = Field(..., description="Autorisation de travail (EU/Visa/No)")
    fit_score_overall: float = Field(..., ge=0, le=100, description="Score global")
    fit_scores: Dict[str, float] = Field(..., description="Scores détaillés par critère")
    
    @field_validator('fit_scores')
    @classmethod
    def validate_fit_scores(cls, v):
        for key, score in v.items():
            if not (0 <= score <= 100):
                raise ValueError(f'Score {key} doit être entre 0 et 100')
        return v
    
    @field_validator('work_authorization')
    @classmethod
    def validate_work_authorization(cls, v):
        if v not in ['EU', 'Visa', 'No']:
            raise ValueError('work_authorization doit être EU, Visa ou No')
        return v


class CVAnalysisService:
    """Service d'analyse de CV avec Claude"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.model_version = f"claude-{self.model}-v1.0"
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            # Essayer d'abord l'extraction de texte normale
            text = extract_text(BytesIO(file_content))
            
            # Vérifier si le texte extrait est vide ou ne contient que des espaces
            if text and text.strip():
                print(f"Extraction PDF normale réussie: {len(text)} caractères")
                return text
            
            print("PDF sans texte extractible - PDF probablement scanné")
            # Au lieu d'OCR, on va utiliser Claude directement avec le PDF
            raise ValueError("PDF_SCANNED")  # Signal spécial pour utiliser Claude directement
            
        except Exception as e:
            if str(e) == "PDF_SCANNED":
                raise e  # Re-raise le signal
            raise ValueError(f"Erreur lors de l'extraction du PDF: {str(e)}")
    
    def extract_text_with_ocr(self, file_content: bytes) -> str:
        """Extrait le texte d'un PDF scanné avec OCR"""
        try:
            print("Test de disponibilité Tesseract...")
            # Test de Tesseract
            try:
                pytesseract.get_tesseract_version()
                print("Tesseract trouvé et fonctionnel")
            except Exception as e:
                raise ValueError(f"Tesseract non trouvé: {str(e)}. Téléchargez et installez Tesseract depuis https://github.com/UB-Mannheim/tesseract/wiki")
            
            print("Conversion PDF en images...")
            # Convertir PDF en images avec gestion d'erreur poppler
            try:
                images = convert_from_bytes(file_content, dpi=150)  # Réduit la résolution pour plus de rapidité
                print(f"Conversion réussie: {len(images)} page(s)")
            except Exception as e:
                raise ValueError(f"Erreur conversion PDF: {str(e)}. Poppler-utils requis pour convertir PDF en images.")
            
            extracted_text = []
            print(f"Traitement OCR de {len(images)} page(s)...")
            
            # Traiter chaque page avec OCR
            for i, image in enumerate(images):
                print(f"OCR page {i+1}/{len(images)}...")
                try:
                    # Utiliser Tesseract pour extraire le texte
                    text = pytesseract.image_to_string(image, lang='fra+eng', config='--psm 6')
                    if text.strip():
                        extracted_text.append(text.strip())
                        print(f"Page {i+1}: {len(text)} caractères extraits")
                except Exception as e:
                    print(f"Erreur OCR page {i+1}: {str(e)}")
                    continue
            
            final_text = '\n\n'.join(extracted_text)
            
            if not final_text.strip():
                raise ValueError("OCR n'a pas pu extraire de texte du PDF scanné")
            
            print(f"OCR réussi: {len(final_text)} caractères extraits au total")
            return final_text
            
        except Exception as e:
            raise ValueError(f"Erreur OCR: {str(e)}. Utilisez le formulaire texte à la place.")
    
    def create_analysis_prompt(self, cv_text: str) -> str:
        """Crée le prompt pour l'analyse du CV"""
        return f"""
Tu es un analyste RH expert. Analyse ce CV et extrais les informations suivantes au format JSON strict.

CONTRAINTES IMPORTANTES:
- Réponds UNIQUEMENT en JSON valide, sans texte additionnel
- Tous les scores doivent être entre 0 et 100
- work_authorization: 'EU', 'Visa', ou 'No'
- availability_date format: 'YYYY-MM-DD' ou null
- languages format: [{{"code_langue": "niveau"}}] ex: [{{"fr": "C2"}}, {{"en": "B2"}}]
- experiences format: [{{"company": "nom", "position": "poste", "duration": "période", "description": "description courte"}}]
- education format: [{{"school": "école", "degree": "diplôme", "duration": "période", "field": "domaine"}}]

CRITÈRES D'ÉVALUATION pour fit_scores:
- skills: Pertinence et niveau des compétences techniques
- experience: Années d'expérience et qualité des postes
- education: Niveau et pertinence de la formation
- culture: Adaptabilité culturelle et soft skills
- overall: Adéquation globale au poste

CV À ANALYSER:
{cv_text}

JSON ATTENDU:
{{
  "headline": "string (titre professionnel accrocheur)",
  "summary": "string (résumé en 2-3 phrases du profil et parcours du candidat)",
  "years_experience": float,
  "experiences": [
    {{"company": "TechCorp", "position": "Senior Developer", "duration": "2020-2024", "description": "Développement d'applications web"}}
  ],
  "skills_primary": ["skill1", "skill2", "skill3"],
  "skills_secondary": ["skill4", "skill5"],
  "languages": [{{"fr": "C2"}}, {{"en": "B2"}}],
  "education_highest": "string (ex: Master Informatique)",
  "education": [
    {{"school": "Université Paris", "degree": "Master Informatique", "duration": "2016-2018", "field": "Intelligence Artificielle"}}
  ],
  "interests": ["sport", "lecture", "voyages"],
  "locations_preferred": ["Paris", "Remote"],
  "salary_expectation_min": int_ou_null,
  "salary_expectation_max": int_ou_null,
  "availability_date": "YYYY-MM-DD_ou_null",
  "work_authorization": "EU|Visa|No",
  "fit_score_overall": float_0_100,
  "fit_scores": {{
    "skills": float_0_100,
    "experience": float_0_100,
    "education": float_0_100,
    "culture": float_0_100
  }}
}}
"""
    
    def analyze_cv_with_pdf_direct(self, file_content: bytes) -> CVAnalysisResponse:
        """Analyse le PDF directement avec Claude (sans extraction de texte)"""
        if not settings.ANTHROPIC_API_KEY:
            # Mode test - analyser avec texte factice
            return self._mock_analysis_response("CV PDF scanné - analyse factice")
            
        try:
            import base64
            
            # Encoder le PDF en base64
            pdf_base64 = base64.b64encode(file_content).decode('utf-8')
            
            prompt = f"""
Tu es un analyste RH expert. Analyse ce CV PDF et extrais les informations suivantes au format JSON strict.

CONTRAINTES IMPORTANTES:
- Réponds UNIQUEMENT en JSON valide, sans texte additionnel
- Tous les scores doivent être entre 0 et 100
- work_authorization: 'EU', 'Visa', ou 'No'
- availability_date format: 'YYYY-MM-DD' ou null
- languages format: [{{"code_langue": "niveau"}}] ex: [{{"fr": "C2"}}, {{"en": "B2"}}]
- experiences format: [{{"company": "nom", "position": "poste", "duration": "période", "description": "description courte"}}]
- education format: [{{"school": "école", "degree": "diplôme", "duration": "période", "field": "domaine"}}]

CRITÈRES D'ÉVALUATION pour fit_scores:
- skills: Pertinence et niveau des compétences techniques
- experience: Années d'expérience et qualité des postes
- education: Niveau et pertinence de la formation
- culture: Adaptabilité culturelle et soft skills
- overall: Adéquation globale au poste

JSON ATTENDU:
{{
  "headline": "string (titre professionnel accrocheur)",
  "summary": "string (résumé en 2-3 phrases du profil et parcours du candidat)",
  "years_experience": float,
  "experiences": [
    {{"company": "TechCorp", "position": "Senior Developer", "duration": "2020-2024", "description": "Développement d'applications web"}}
  ],
  "skills_primary": ["skill1", "skill2", "skill3"],
  "skills_secondary": ["skill4", "skill5"],
  "languages": [{{"fr": "C2"}}, {{"en": "B2"}}],
  "education_highest": "string (ex: Master Informatique)",
  "education": [
    {{"school": "Université Paris", "degree": "Master Informatique", "duration": "2016-2018", "field": "Intelligence Artificielle"}}
  ],
  "interests": ["sport", "lecture", "voyages"],
  "locations_preferred": ["Paris", "Remote"],
  "salary_expectation_min": int_ou_null,
  "salary_expectation_max": int_ou_null,
  "availability_date": "YYYY-MM-DD_ou_null",
  "work_authorization": "EU|Visa|No",
  "fit_score_overall": float_0_100,
  "fit_scores": {{
    "skills": float_0_100,
    "experience": float_0_100,
    "education": float_0_100,
    "culture": float_0_100
  }}
}}
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            }
                        ]
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Parse le JSON
            analysis_data = json.loads(content)
            
            # Valide avec Pydantic
            return CVAnalysisResponse(**analysis_data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Réponse Claude invalide (JSON): {str(e)}")
        except Exception as e:
            error_msg = str(e)
            if "credit balance is too low" in error_msg:
                raise ValueError("Crédits Claude insuffisants. Ajoutez des crédits sur https://console.anthropic.com/settings/billing")
            else:
                raise ValueError(f"Erreur lors de l'analyse IA avec PDF: {error_msg}")

    def analyze_cv_with_ai(self, cv_text: str) -> CVAnalysisResponse:
        """Analyse le CV avec Claude et retourne les données structurées"""
        # Mode test - retourne des données factices si pas de clé API
        if not settings.ANTHROPIC_API_KEY:
            return self._mock_analysis_response(cv_text)
            
        try:
            prompt = self.create_analysis_prompt(cv_text)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Parse le JSON
            analysis_data = json.loads(content)
            
            # Valide avec Pydantic
            return CVAnalysisResponse(**analysis_data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Réponse Claude invalide (JSON): {str(e)}")
        except Exception as e:
            # Si c'est un problème de crédits, on le signale clairement
            error_msg = str(e)
            if "credit balance is too low" in error_msg:
                raise ValueError("Crédits Claude insuffisants. Ajoutez des crédits sur https://console.anthropic.com/settings/billing")
            else:
                raise ValueError(f"Erreur lors de l'analyse IA: {error_msg}")
    
    def _mock_analysis_response(self, cv_text: str) -> CVAnalysisResponse:
        """Génère une réponse fictive pour les tests"""
        import re
        
        # Analyse basique du texte pour extraire des infos
        lines = cv_text.split('\n')
        text_lower = cv_text.lower()
        
        # Essayer de détecter le nom (première ligne non vide)
        headline = "Professionnel expérimenté"
        for line in lines:
            line = line.strip()
            if line and not line.lower().startswith(('cv', 'curriculum', 'resume')):
                if len(line.split()) <= 6 and not any(keyword in line.lower() for keyword in ['email', '@', 'tel', 'phone']):
                    headline = line
                    break
        
        # Détecter les années d'expérience
        years_exp = 3.0
        exp_patterns = [
            r'(\d+)\s*(?:ans?|years?)\s*(?:d[\'e]|of)?\s*(?:expérience|experience)',
            r'(?:expérience|experience).*?(\d+)\s*(?:ans?|years?)',
            r'(\d+)\+?\s*(?:ans?|years?)'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years_exp = float(matches[0])
                break
        
        # Extraire compétences avec priorités
        skills_primary = []
        skills_secondary = []
        
        # Compétences techniques courantes avec catégories
        tech_skills = {
            'python': 'Python',
            'javascript': 'JavaScript',
            'react': 'React',
            'django': 'Django',
            'node': 'Node.js',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'sql': 'SQL',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'git': 'Git',
            'docker': 'Docker',
            'aws': 'AWS',
            'azure': 'Azure',
            'java': 'Java',
            'php': 'PHP',
            'html': 'HTML/CSS',
            'css': 'HTML/CSS'
        }
        
        # Rechercher les compétences dans le texte
        found_skills = []
        for skill_key, skill_name in tech_skills.items():
            if skill_key in text_lower:
                found_skills.append(skill_name)
        
        # Répartir entre primaires et secondaires
        skills_primary = found_skills[:5] if found_skills else ['Web Development', 'Software Engineering', 'Programming']
        skills_secondary = found_skills[5:10] if len(found_skills) > 5 else []
        
        # Détecter l'éducation
        education = "Formation supérieure"
        education_patterns = [
            r'master', r'ingénieur', r'bac\+5', r'm2', r'm1',
            r'licence', r'bachelor', r'bac\+3', r'l3',
            r'bts', r'dut', r'bac\+2'
        ]
        
        for pattern in education_patterns:
            if re.search(pattern, text_lower):
                if pattern in ['master', 'ingénieur', 'bac+5', 'm2']:
                    education = "Master / Ingénieur"
                elif pattern in ['licence', 'bachelor', 'bac+3', 'l3']:
                    education = "Licence / Bachelor"
                elif pattern in ['bts', 'dut', 'bac+2']:
                    education = "BTS / DUT"
                break
        
        # Calculer des scores basés sur le contenu
        base_score = 70.0
        
        # Bonus pour expérience
        exp_bonus = min(years_exp * 5, 20)  # Max 20 points
        
        # Bonus pour compétences
        skills_bonus = min(len(skills_primary) * 2, 15)  # Max 15 points
        
        overall_score = min(base_score + exp_bonus + skills_bonus, 95.0)
        
        return CVAnalysisResponse(
            headline=headline,
            summary=f"Professionnel avec {years_exp} ans d'expérience, spécialisé en développement logiciel. Expertise en {', '.join(skills_primary[:3]) if skills_primary else 'technologies modernes'}.",
            years_experience=years_exp,
            experiences=[
                {"company": "TechCorp", "position": "Développeur Senior", "duration": "2021-2024", "description": "Développement d'applications web"},
                {"company": "StartupXYZ", "position": "Développeur", "duration": "2019-2021", "description": "Développement full-stack"}
            ],
            skills_primary=skills_primary,
            skills_secondary=skills_secondary,
            languages=[{"fr": "C2"}, {"en": "B2"}],
            education_highest=education,
            education=[
                {"school": "Université", "degree": education, "duration": "2016-2018", "field": "Informatique"}
            ],
            interests=["Technologie", "Innovation", "Open Source"],
            locations_preferred=["Paris", "Lyon", "Remote"],
            salary_expectation_min=None,
            salary_expectation_max=None,
            availability_date=None,
            work_authorization="EU",
            fit_score_overall=overall_score,
            fit_scores={
                "skills": min(overall_score + 5, 95.0),
                "experience": min(base_score + exp_bonus, 90.0),
                "education": min(75.0, 85.0),
                "culture": overall_score - 5
            }
        )
    
    def analyze_cv_from_file(self, file_path: str) -> tuple[CVAnalysisResponse, str]:
        """
        Analyse un CV depuis un fichier
        
        Returns:
            tuple: (CVAnalysisResponse, model_version)
        """
        # Lecture du fichier
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Extraction du texte
        cv_text = self.extract_text_from_pdf(file_content)
        
        if not cv_text.strip():
            raise ValueError("Aucun texte extractible du fichier PDF")
        
        # Analyse IA
        analysis = self.analyze_cv_with_ai(cv_text)
        
        return analysis, self.model_version
    
    def analyze_cv_from_bytes(self, file_content: bytes) -> tuple[CVAnalysisResponse, str]:
        """
        Analyse un CV depuis des bytes (pour upload direct)
        
        Returns:
            tuple: (CVAnalysisResponse, model_version)
        """
        try:
            # Essayer d'abord l'extraction de texte
            cv_text = self.extract_text_from_pdf(file_content)
            print(f"Extraction de texte réussie: {len(cv_text)} caractères")
            
            if not cv_text.strip():
                raise ValueError("Aucun texte extractible du fichier PDF")
            
            # Analyse IA avec texte extrait
            analysis = self.analyze_cv_with_ai(cv_text)
            
        except ValueError as e:
            if str(e) == "PDF_SCANNED":
                # PDF scanné - analyse directe avec Claude
                print("PDF scanné détecté - analyse directe avec Claude...")
                analysis = self.analyze_cv_with_pdf_direct(file_content)
            else:
                # Autre erreur - re-raise
                raise e
        
        return analysis, self.model_version


def create_candidature_from_analysis(analysis: CVAnalysisResponse, model_version: str, resume_url: str) -> dict:
    """
    Convertit une analyse en données pour créer une Candidature
    
    Args:
        analysis: Résultat de l'analyse CV
        model_version: Version du modèle utilisé
        resume_url: URL du CV
    
    Returns:
        dict: Données prêtes pour Candidature.objects.create()
    """
    from .models import WorkAuthorizationChoices, StatusChoices, PriorityChoices
    
    # Mapping work_authorization
    work_auth_mapping = {
        'EU': WorkAuthorizationChoices.EU,
        'Visa': WorkAuthorizationChoices.VISA,
        'No': WorkAuthorizationChoices.NO
    }
    
    data = {
        'resume': resume_url,
        'cv_url': resume_url,  # URL du CV original
        'headline': analysis.headline,
        'summary': analysis.summary,
        'years_experience': Decimal(str(analysis.years_experience)),
        'experiences': analysis.experiences,
        'skills_primary': analysis.skills_primary,
        'skills_secondary': analysis.skills_secondary,
        'languages': analysis.languages,
        'education_highest': analysis.education_highest,
        'education': analysis.education,
        'interests': analysis.interests,
        'locations_preferred': analysis.locations_preferred,
        'salary_expectation_min': analysis.salary_expectation_min,
        'salary_expectation_max': analysis.salary_expectation_max,
        'work_authorization': work_auth_mapping.get(analysis.work_authorization, WorkAuthorizationChoices.EU),
        'status': StatusChoices.SUBMITTED,
        'priority': PriorityChoices.NORMAL,
        'fit_score_overall': Decimal(str(analysis.fit_score_overall)),
        'fit_scores': analysis.fit_scores,
        'model_version': model_version,
        'analyzed_at': datetime.now(),
    }
    
    # Gestion de la date de disponibilité
    if analysis.availability_date:
        try:
            from datetime import datetime as dt
            data['availability_date'] = dt.strptime(analysis.availability_date, '%Y-%m-%d').date()
        except ValueError:
            pass  # Ignore les dates mal formatées
    
    return data