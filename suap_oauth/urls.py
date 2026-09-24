from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import SuapProvider


urlpatterns = default_urlpatterns(SuapProvider)
