from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
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
                    analysis_result, model_version = service.analyze_cv_from_bytes(file_content)
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
            
            # Retourner les résultats de l'analyse
            return JsonResponse({
                'status': 'success',
                'candidature_id': str(candidature.id),
                'analysis': {
                    'headline': analysis_result.headline,
                    'years_experience': float(analysis_result.years_experience),
                    'skills_primary': analysis_result.skills_primary,
                    'skills_secondary': analysis_result.skills_secondary,
                    'education': analysis_result.education_highest,
                    'languages': analysis_result.languages,
                    'locations': analysis_result.locations_preferred,
                    'salary_min': analysis_result.salary_expectation_min,
                    'salary_max': analysis_result.salary_expectation_max,
                    'availability': analysis_result.availability_date,
                    'work_authorization': analysis_result.work_authorization,
                    'fit_score': float(analysis_result.fit_score_overall),
                    'fit_scores': {
                        k: float(v) for k, v in analysis_result.fit_scores.items()
                    }
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