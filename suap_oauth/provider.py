from allauth.account.models import EmailAddress
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from .views import SuapOAuth2Adapter
from usuarios.models import Vinculos
from re import sub


class SuapAccount(ProviderAccount):
    pass
    # def get_profile_url(self):
        # return self.account.extra_data.get("html_url")

    # def get_avatar_url(self):
        # return self.account.extra_data.get("avatar_url")


class SuapProvider(OAuth2Provider):
    id = "suap"
    name = "SUAP"
    account_class = SuapAccount
    oauth2_adapter_class = SuapOAuth2Adapter

    def get_default_scope(self):
        scope = ["identificacao", "email", "documentos_pessoais"]
        return scope

    def extract_uid(self, data):
        return str(sub(r"\D","",data.get('cpf')))

    def extract_common_fields(self, data):
        nome_completo = data.get('nome_registro')
        if nome_social := data.get('nome_social'):
            nome_completo = nome_social
        primeiro_nome, *_, ultimo_nome = nome_completo.split()
        curso = response.get('curso') if data.get('curso') else ""
        if "Servidor" in data.get('tipo_usuario'):
            vinculo = Vinculos.SERVIDOR
        else:
            vinculo = Vinculos.ALUNO
        return dict(
            nome_completo=nome_completo,
            email=data.get("email_preferencial"),
            username=data.get('email_preferencial'),
            cpf=sub(r"\D","",data.get('cpf')),
            matricula=data.get('identificacao'),
            first_name=primeiro_nome,
            last_name=ultimo_nome,
            campus=data.get('campus'),
            curso=curso,
            vinculo=vinculo,
            instituicao="IFRN",
        )


provider_classes = [SuapProvider]
