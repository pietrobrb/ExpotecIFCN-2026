from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field


class SuapAdapter(DefaultSocialAccountAdapter):
    
    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.

        For convenience, we populate several common fields.

        Note that the user instance being populated represents a
        suggested User instance that represents the social user that is
        in the process of being logged in.

        The User instance need not be completely valid and conflict
        free. For example, verifying whether or not the username
        already exists, is not a responsibility.
        """
        user = sociallogin.user
        user_email(user, data.get("email") or "")
        user_field(user, "username", data.get("username"))
        user_field(user, "nome_completo", data.get("nome_completo"))
        user_field(user, "first_name", data.get("first_name"))
        user_field(user, "last_name", data.get("last_name"))
        user_field(user, "cpf", data.get("cpf"))
        user_field(user, "instituicao", data.get("instituicao"))
        user_field(user, "vinculo", data.get("vinculo"))
        user_field(user, "matricula", data.get("matricula"))
        user_field(user, "campus", data.get("campus"))
        user_field(user, "curso", data.get("curso"))
        return user
