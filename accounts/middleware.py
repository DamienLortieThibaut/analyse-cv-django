from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings

User = get_user_model()

class JWTAuthenticationMiddleware:
    """
    Middleware pour l'authentification JWT via les cookies
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Récupérer le token depuis les cookies
        access_token = request.COOKIES.get('access_token')
        
        if access_token:
            try:
                # Valider le token
                UntypedToken(access_token)
                
                # Décoder le token pour récupérer l'ID utilisateur
                payload = jwt.decode(
                    access_token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                
                user_id = payload.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                    except User.DoesNotExist:
                        request.user = AnonymousUser()
                else:
                    request.user = AnonymousUser()
                    
            except (InvalidToken, TokenError, jwt.ExpiredSignatureError, jwt.DecodeError):
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response
