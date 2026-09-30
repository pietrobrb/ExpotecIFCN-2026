from allauth.account.models import EmailAddress
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from .views import SuapOAuth2Adapter
from usuarios.models import Vinculos
from re import sub


class SuapAccount(ProviderAccount):
    pass


class SuapProvider(OAuth2Provider):
    id = "suap"
    name = "SUAP"
    account_class = SuapAccount
    oauth2_adapter_class = SuapOAuth2Adapter

    def get_default_scope(self):
        scope = ["identificacao", "email", "documentos_pessoais"]
        return scope

    def extract_uid(self, data):
        cpf = data.get("cpf")
        if cpf:
            return str(sub(r"\D", "", cpf))

        identificacao = (
            data.get("identificacao")
            or data.get("email_preferencial")
            or data.get("email")
            or ""
        ).strip()

        if not identificacao:
            raise ValueError("SUAP payload sem cpf/identificacao/email")

        return str(identificacao)

    def extract_common_fields(self, data):
        nome_completo = (
            data.get("nome_registro")
            or data.get("nome_social")
            or data.get("nome")
            or ""
        ).strip()
        nomes = nome_completo.split()

        if nomes:
            primeiro_nome = nomes[0]
            ultimo_nome = nomes[-1] if len(nomes) > 1 else ""
        else:
            primeiro_nome = "Usuário"
            ultimo_nome = ""

        tipo_usuario = data.get("tipo_usuario") or ""
        vinculo = Vinculos.SERVIDOR if "Servidor" in tipo_usuario else Vinculos.ALUNO

        email = data.get("email_preferencial") or data.get("email") or ""

        return dict(
            nome_completo=nome_completo or "Usuário",
            email=email,
            username=email,
            cpf=sub(r"\D", "", (data.get("cpf") or "")),
            matricula=data.get("identificacao"),
            first_name=primeiro_nome,
            last_name=ultimo_nome,
            campus=data.get("campus"),
            curso=data.get("curso") or "",
            vinculo=vinculo,
            instituicao="IFRN",
        )


provider_classes = [SuapProvider]