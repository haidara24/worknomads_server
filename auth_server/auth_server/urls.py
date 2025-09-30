from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.http import JsonResponse
from jwcrypto import jwk
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
]

# JWKS endpoint — return JWK Set built from the public key
def jwks_view(request):
    pub = settings.JWT_PUBLIC_KEY
    if not pub:
        return JsonResponse({"keys": []})

    key = jwk.JWK.from_pem(pub.encode("utf-8"))
    jwk_dict = key.export_public(as_dict=True)
    # ensure 'kid' present — use a simple kid derived from thumbprint
    if "kid" not in jwk_dict:
        jwk_dict["kid"] = key.thumbprint()
    jwks = {"keys": [jwk_dict]}
    return JsonResponse(jwks)

urlpatterns += [
    path(".well-known/jwks.json", jwks_view, name="jwks"),
]
