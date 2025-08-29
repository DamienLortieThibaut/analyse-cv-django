from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import models
from .forms import CandidatureUploadForm
from .models import Candidature
from .services import CVAnalysisService, create_candidature_from_analysis
import json
import uuid


class CandidatureUploadView(View):
    template_name = 'candidatures/upload.html'
    
    def get(self, request):
        form = CandidatureUploadForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        # Nettoyer les données de session précédentes
        if 'pending_candidature' in request.session:
            del request.session['pending_candidature']
            
        form = CandidatureUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Save uploaded file to MinIO
                cv_file = form.cleaned_data['cv_file']
                file_name = f"cv_{uuid.uuid4()}_{cv_file.name}"
                file_path = f"cvs/{file_name}"
                
                # Save to MinIO
                saved_path = default_storage.save(file_path, ContentFile(cv_file.read()))
                file_url = default_storage.url(saved_path)
                
                # Store form data in session for analysis
                request.session['pending_candidature'] = {
                    'email': form.cleaned_data['email'],
                    'cv_file_path': saved_path,
                    'cv_file_url': file_url,
                    'uploaded_at': timezone.now().isoformat()
                }
                
                messages.success(request, "CV uploadé avec succès ! L'analyse va commencer...")
                return redirect('candidatures:analyze')
                
            except Exception as e:
                messages.error(request, f"Erreur lors de l'upload : {str(e)}")
                return render(request, self.template_name, {'form': form})
        
        return render(request, self.template_name, {'form': form})


class CandidatureTestTextView(View):
    template_name = 'candidatures/test_text.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        try:
            # Nettoyer les données de session précédentes
            if 'pending_candidature' in request.session:
                del request.session['pending_candidature']
            
            # Récupérer les données du formulaire
            email = request.POST.get('email')
            cv_text = request.POST.get('cv_text')
            
            if not all([email, cv_text]):
                messages.error(request, "L'email et le CV sont obligatoires")
                return render(request, self.template_name)
            
            print(f"Text form - données reçues: email={email}")
            print(f"Text form - longueur cv_text: {len(cv_text)} caractères")
            
            # Store form data in session for analysis
            session_data = {
                'email': email,
                'cv_text': cv_text,  # Texte direct au lieu d'un fichier
                'cv_file_url': f'#text-cv-{uuid.uuid4()}',
                'uploaded_at': timezone.now().isoformat()
            }
            request.session['pending_candidature'] = session_data
            
            print(f"Text form - session stockée avec clés: {list(session_data.keys())}")
            print(f"Text form - vérification: 'cv_text' in session = {'cv_text' in session_data}")
            
            # Force session save
            request.session.save()
            
            messages.success(request, "Texte reçu ! L'analyse va commencer...")
            return redirect('candidatures:analyze')
            
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")
            return render(request, self.template_name)


class CandidatureAnalyzeView(TemplateView):
    template_name = 'candidatures/analyze.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pending = self.request.session.get('pending_candidature', {})
        context['candidature_data'] = pending
        return context


class CandidatureAnalyzeAPIView(View):
    """API endpoint pour lancer l'analyse du CV avec Claude"""
    
    def post(self, request):
        try:
            # Récupérer les données de la session
            pending_data = request.session.get('pending_candidature')
            if not pending_data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Aucune candidature en attente'
                }, status=400)
            
            print("Données en session:", pending_data.keys())
            print("Contenu session complète:", pending_data)
            
            # Analyser selon le type (fichier ou texte)
            try:
                service = CVAnalysisService()
                
                if 'cv_text' in pending_data:
                    # Mode test texte - analyse directe
                    cv_text = pending_data['cv_text']
                    print(f"Mode texte détecté - Analyse de {len(cv_text)} caractères")
                    print("Première ligne du texte:", cv_text[:100] if cv_text else "VIDE")
                    analysis_result = service.analyze_cv_with_ai(cv_text)
                    model_version = service.model_version
                    print("Analyse texte terminée avec succès")
                elif 'cv_file_path' in pending_data:
                    # Mode fichier PDF
                    file_path = pending_data['cv_file_path']
                    print(f"Mode fichier détecté - {file_path}")
                    file_content = default_storage.open(file_path).read()
                    
                    # Extraire le nom de fichier original pour aider l'analyse
                    import os
                    filename = os.path.basename(file_path)
                    print(f"Nom de fichier original: {filename}")
                    
                    analysis_result, model_version = service.analyze_cv_from_bytes(file_content, filename)
                    print("Analyse fichier terminée avec succès")
                else:
                    print("ERREUR: Aucune donnée CV trouvée dans la session")
                    print("Clés disponibles:", list(pending_data.keys()) if pending_data else "Session vide")
                    raise ValueError("Aucune donnée CV trouvée (ni texte ni fichier)")
                    
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erreur analyse CV: {str(e)}'
                }, status=500)
            
            # Créer la candidature
            try:
                candidature_data = create_candidature_from_analysis(
                    analysis_result,
                    model_version,
                    pending_data['cv_file_url']
                )
                
                # Ajouter les données du formulaire (les noms viennent maintenant de l'analyse Claude)
                candidature_data['email'] = pending_data['email']
                candidature_data['phone'] = ''
                candidature_data['position_applied'] = ''
                candidature_data['message'] = ''
                
                # Créer l'objet Candidature
                candidature = Candidature.objects.create(**candidature_data)
                
                # Nettoyer la session
                del request.session['pending_candidature']
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Erreur création candidature: {str(e)}'
                }, status=500)
            
            # Retourner les résultats de l'analyse avec TOUTES les données
            return JsonResponse({
                'status': 'success',
                'candidature_id': str(candidature.id),
                'candidate': {
                    'first_name': analysis_result.first_name,
                    'last_name': analysis_result.last_name,
                    'full_name': f"{analysis_result.first_name} {analysis_result.last_name}",
                    'headline': analysis_result.headline,
                    'summary': analysis_result.summary,
                },
                'experience': {
                    'years_total': float(analysis_result.years_experience),
                    'experiences': analysis_result.experiences,
                },
                'education': {
                    'highest_degree': analysis_result.education_highest,
                    'education_details': analysis_result.education,
                },
                'skills': {
                    'primary': analysis_result.skills_primary,
                    'secondary': analysis_result.skills_secondary,
                },
                'languages': analysis_result.languages,
                'personal': {
                    'interests': analysis_result.interests,
                    'locations_preferred': analysis_result.locations_preferred,
                    'availability_date': analysis_result.availability_date,
                    'work_authorization': analysis_result.work_authorization,
                },
                'salary': {
                    'expectation_min': analysis_result.salary_expectation_min,
                    'expectation_max': analysis_result.salary_expectation_max,
                },
                'scoring': {
                    'fit_score_overall': float(analysis_result.fit_score_overall),
                    'fit_scores_detailed': {
                        k: float(v) for k, v in analysis_result.fit_scores.items()
                    }
                },
                'metadata': {
                    'analyzed_at': candidature.analyzed_at.isoformat() if candidature.analyzed_at else None,
                    'model_version': model_version,
                },
                'redirect_url': f'/candidatures/{candidature.id}/'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Erreur lors de l'analyse : {str(e)}"
            }, status=500)


class CandidatureSuccessView(TemplateView):
    template_name = 'candidatures/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidature_id = self.kwargs.get('candidature_id')
        
        try:
            candidature = Candidature.objects.get(id=candidature_id)
            context['candidature'] = candidature
        except Candidature.DoesNotExist:
            context['candidature'] = None
            
        return context


class CandidatureListView(ListView):
    model = Candidature
    template_name = 'candidatures/list.html'
    context_object_name = 'candidatures'
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtrer par id utilisateur depuis l'URL si présent
        user_id_filter = self.kwargs.get('id')
        if user_id_filter:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id_filter)
                qs = qs.filter(email=user.email)
            except (User.DoesNotExist, ValueError):
                # Si l'utilisateur n'existe pas, retourner queryset vide
                qs = qs.none()

        # Filtres basiques (statut, score, expérience, recherche)
        status = self.request.GET.get('status')
        score_min = self.request.GET.get('score_min')
        experience = self.request.GET.get('experience')
        search = self.request.GET.get('search')

        if status:
            qs = qs.filter(status=status)
        if score_min:
            try:
                qs = qs.filter(fit_score_overall__gte=float(score_min))
            except ValueError:
                pass
        if experience:
            if experience == '0-2':
                qs = qs.filter(years_experience__gte=0, years_experience__lte=2)
            elif experience == '3-5':
                qs = qs.filter(years_experience__gte=3, years_experience__lte=5)
            elif experience == '6-10':
                qs = qs.filter(years_experience__gte=6, years_experience__lte=10)
            elif experience == '10+':
                qs = qs.filter(years_experience__gte=10)
        if search:
            qs = qs.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(headline__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter l'id utilisateur filtré au contexte pour l'affichage
        user_id_filter = self.kwargs.get('id')
        if user_id_filter:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id_filter)
                context['user_filter'] = user
                context['id_filter'] = user_id_filter
            except User.DoesNotExist:
                context['user_filter'] = None
                context['id_filter'] = user_id_filter
        return context

