from re import sub

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from usuarios.models import Vinculos

from .views import SuapOAuth2Adapter


class SuapAccount(ProviderAccount):
    pass


class SuapProvider(OAuth2Provider):
    id = "suap"
    name = "SUAP"
    account_class = SuapAccount
    oauth2_adapter_class = SuapOAuth2Adapter

    def get_default_scope(self):
        return [
            "identificacao",
            "email",
            "documentos_pessoais",
        ]

    def extract_uid(self, data):
        cpf = data.get("cpf")

        if cpf:
            cpf_limpo = sub(r"\D", "", cpf)

            if cpf_limpo:
                return cpf_limpo

        identificacao = (
            data.get("identificacao")
            or data.get("email_preferencial")
            or data.get("email")
            or ""
        ).strip()

        if not identificacao:
            raise ValueError(
                "SUAP payload sem cpf, identificacao ou email"
            )

        return str(identificacao)

    def extract_common_fields(self, data):
        nome_completo = (
            data.get("nome_social")
            or data.get("nome_usual")
            or data.get("nome_registro")
            or data.get("nome")
            or ""
        ).strip()

        primeiro_nome = (
            data.get("primeiro_nome")
            or ""
        ).strip()

        ultimo_nome = (
            data.get("ultimo_nome")
            or ""
        ).strip()

        if not primeiro_nome:
            nomes = nome_completo.split()
            primeiro_nome = nomes[0] if nomes else "Usuário"

        if not ultimo_nome:
            nomes = nome_completo.split()
            ultimo_nome = nomes[-1] if len(nomes) > 1 else ""

        tipo_usuario = (
            data.get("tipo_usuario")
            or ""
        ).strip()

        if "Servidor" in tipo_usuario:
            vinculo = Vinculos.SERVIDOR
        else:
            vinculo = Vinculos.ALUNO

        email = (
            data.get("email_preferencial")
            or data.get("email")
            or ""
        ).strip()

        cpf = sub(
            r"\D",
            "",
            data.get("cpf") or "",
        )

        return {
            "nome_completo": nome_completo or "Usuário",
            "email": email,
            "username": email,
            "cpf": cpf,
            "matricula": data.get("identificacao"),
            "first_name": primeiro_nome,
            "last_name": ultimo_nome,
            "campus": data.get("campus"),
            "curso": "",
            "vinculo": vinculo,
            "instituicao": "IFRN",
        }


provider_classes = [SuapProvider]
