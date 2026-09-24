from typing import Optional

from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class SuapOAuth2Adapter(OAuth2Adapter):
    provider_id = "suap"
    settings = app_settings.PROVIDERS.get(provider_id, {})

    if "SUAP_URL" in settings:
        web_url = settings.get("SUAP_URL").rstrip("/")
        api_url = "{0}/api".format(web_url)
    else:
        web_url = "https://suap.ifrn.edu.br"
        api_url = "https://suap.ifrn.edu.br/api"

    access_token_url = "{0}/o/token/".format(web_url)
    authorize_url = "{0}/o/authorize/".format(web_url)
    profile_url = "{0}/eu/".format(api_url)

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(SuapOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SuapOAuth2Adapter)
