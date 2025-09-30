import time
import requests
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from jwcrypto import jwk
from django.conf import settings
from rest_framework import authentication, exceptions

class JWKSCache:
    _jwks = None
    _last_fetched = 0

    @classmethod
    def get_jwks(cls):
        now = int(time.time())
        if cls._jwks is None or (now - cls._last_fetched) > settings.JWKS_REFRESH_INTERVAL_SECONDS:
            try:
                resp = requests.get(settings.JWKS_URL, timeout=5)
                resp.raise_for_status()
                cls._jwks = resp.json()
                cls._last_fetched = now
            except Exception as e:
                if cls._jwks:
                    return cls._jwks
                raise e
        return cls._jwks

    @classmethod
    def get_public_key_for_kid(cls, kid):
        jwks = cls.get_jwks()
        keys = jwks.get("keys", [])
        for key_dict in keys:
            if key_dict.get("kid") == kid:
                jwk_key = jwk.JWK.from_json(json.dumps(key_dict))
                pem = jwk_key.export_to_pem(private_key=False)
                return pem.decode("utf-8")
        if len(keys) == 1:
            jwk_key = jwk.JWK.from_json(json.dumps(keys[0]))
            pem = jwk_key.export_to_pem(private_key=False)
            return pem.decode("utf-8")
        return None

import json

class RemoteUser:

    def __init__(self, username, payload):
        self.username = username
        self.payload = payload

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username or "remote"

class JWKSAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ", 1)[1].strip()

        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed("Invalid token header")

        kid = unverified_header.get("kid")

        try:
            if kid:
                public_key_pem = JWKSCache.get_public_key_for_kid(kid)
            else:
                jwks = JWKSCache.get_jwks()
                keys = jwks.get("keys", [])
                if not keys:
                    raise exceptions.AuthenticationFailed("No JWKS keys available")
                jwk_key = jwk.JWK.from_json(json.dumps(keys[0]))
                public_key_pem = jwk_key.export_to_pem( private_key=False).decode("utf-8")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Unable to fetch JWKS: {str(e)}")

        if not public_key_pem:
            raise exceptions.AuthenticationFailed("Public key not found for token")

        try:
            payload = jwt.decode(token, public_key_pem, algorithms=["RS256"], options={"verify_aud": False})
        except ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")

        # Prefer standard claims: sub -> username, else use "username" claim
        username = payload.get("sub") or payload.get("username") or payload.get("user_id") or payload.get("preferred_username")
        if username is None:
            raise exceptions.AuthenticationFailed("Token missing subject/username")

        user = RemoteUser(username=username, payload=payload)
        return (user, payload)

    def authenticate_header(self, request):
        return "Bearer"
