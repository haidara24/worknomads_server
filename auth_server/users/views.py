from rest_framework import generics
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views import View
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json
import base64
import hashlib
from django.conf import settings

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class JWKSView(View):
    def get(self, request):
        try:
            # Load the public key
            public_key = serialization.load_pem_public_key(
                settings.JWT_PUBLIC_KEY.encode(),
                backend=default_backend()
            )
            
            # Get public numbers
            public_numbers = public_key.public_numbers()
            
            # Convert to JWKS format
            jwks = {
                "keys": [
                    {
                        "kty": "RSA",
                        "use": "sig",
                        "alg": "RS256",
                        "n": self.int_to_base64url(public_numbers.n),
                        "e": self.int_to_base64url(public_numbers.e),
                        "kid": "auth-server-key-1"
                    }
                ]
            }
            
            return JsonResponse(jwks)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    def int_to_base64url(self, n):
        """Convert integer to Base64URL"""
        # Convert to bytes
        n_bytes = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        # Encode to base64 and convert to URL-safe format
        return base64.urlsafe_b64encode(n_bytes).rstrip(b'=').decode('ascii')