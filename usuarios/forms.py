import re

from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import (
    SignupForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
)

from betterforms.multiform import MultiModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset

from core.forms import ModelSelect2MultipleWidget
from enderecos.forms import EnderecoForm
from eventos.models import AreaTematica, Avaliador, InscricaoEvento
from .models import User, Vinculos

# CADASTRO E AUTENTICAÇÃO

class UserSignupForm(SignupForm):
    nome_completo = forms.CharField(
        max_length=100,
        label="Nome Completo",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nome Completo",
            }
        ),
    )

    vinculo = forms.ChoiceField(
        choices=[
            (member.value, member.label)
            for member in [
                Vinculos.ESTUDANTE,
                Vinculos.PROFISSIONAL,
                Vinculos.OUTRO,
            ]
        ],
        label="Vínculo",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, request):
        user = super().save(request)

        user.nome_completo = self.cleaned_data["nome_completo"]
        user.vinculo = self.cleaned_data["vinculo"]
        user.save()

        return user


class UserLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class UserResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class UserResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

# INSCRIÇÃO NO EVENTO

class InscricaoEventoForm(forms.ModelForm):
    class Meta:
        model = InscricaoEvento
        fields = []

# PERFIL DO USUÁRIO

class PerfilForm(forms.ModelForm):
    cpf = forms.CharField(
        label="CPF",
        max_length=11,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "CPF",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
    )

    foto_perfil = forms.ImageField(
        label="Foto de Perfil (opcional)",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = [
            "nome_completo",
            "cpf",
            "vinculo",
            "foto_perfil",
            "instituicao",
            "matricula",
            "campus",
            "curso",
        ]
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "form-control"}),
            "vinculo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),
            "instituicao": forms.TextInput(attrs={"class": "form-control"}),
            "matricula": forms.TextInput(attrs={"class": "form-control"}),
            "campus": forms.TextInput(attrs={"class": "form-control"}),
            "curso": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_cpf(self):
        cpf = re.sub(
            r"\D",
            "",
            self.cleaned_data.get("cpf", ""),
        )

        if len(cpf) != 11:
            raise forms.ValidationError("O CPF deve conter 11 dígitos.")

        if len(set(cpf)) == 1:
            raise forms.ValidationError("CPF inválido.")

        for quantidade in (9, 10):
            soma = sum(
                int(cpf[posicao]) * (quantidade + 1 - posicao)
                for posicao in range(quantidade)
            )

            digito = (soma * 10 % 11) % 10

            if digito != int(cpf[quantidade]):
                raise forms.ValidationError("CPF inválido.")

        return cpf

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("cpf", css_class="col-md-3"),
                Column("nome_completo", css_class="col-md-6"),
                Column("vinculo", css_class="col-md-3"),
                Column("foto_perfil", css_class="col-md-12"),
                Column("instituicao", css_class="col-md-6"),
                Column("campus", css_class="col-md-6"),
                Column("curso", css_class="col-md-6"),
                Column("matricula", css_class="col-md-6"),
            ),
        )
    )

# FORMULÁRIO COMBINADO DE INSCRIÇÃO

class InscricaoEventoMuiltForm(MultiModelForm):
    form_classes = {
        "usuario": PerfilForm,
        "endereco": EnderecoForm,
        "inscricao": InscricaoEventoForm,
    }

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)

        if instance is not None:
            usuario = instance.usuario

            kwargs["instance"] = {
                "pk": instance.pk,
                "usuario": usuario,
                "endereco": (usuario.endereco if usuario.endereco else None),
            }

        super().__init__(*args, **kwargs)

        self.forms["endereco"].fields["local"].widget = forms.HiddenInput()

# FORMULÁRIO COMBINADO DE EDIÇÃO DO PERFIL

class MeuPerfilMuiltForm(MultiModelForm):
    form_classes = {
        "usuario": PerfilForm,
        "endereco": EnderecoForm,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.forms["endereco"].fields["local"].widget = forms.HiddenInput()

# CADASTRO E EDIÇÃO DE AVALIADORES

class EventoAvaliadorForm(forms.ModelForm):
    areas_tematicas = forms.ModelMultipleChoiceField(
        required=True,
        label="",
        queryset=AreaTematica.objects.all().order_by("nome"),
        widget=forms.CheckboxSelectMultiple(),
    )

    confirmacao = forms.BooleanField(
        label=(
            "Confirmo que estou ciente de que, ao me inscrever "
            "como avaliador, estou apto a avaliar qualquer trabalho "
            "das áreas temáticas selecionadas."
        ),
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Avaliador
        fields = ["areas_tematicas", "confirmacao"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if (
            self.instance
            and self.instance.pk
            and self.instance.areas_tematicas.exists()
        ):
            self.fields["confirmacao"].initial = True

    def clean_confirmacao(self):
        confirmacao = self.cleaned_data.get("confirmacao")

        if not confirmacao:
            raise forms.ValidationError(
                "Você deve confirmar que está ciente das normas "
                "para se inscrever como avaliador."
            )

        return confirmacao

    helper = FormHelper()
    helper.layout = Layout(
        Row(
            Column(
                "areas_tematicas",
                css_class="col-md-12 border-bottom",
            ),
            Column(
                "confirmacao",
                css_class="col-md-12 mt-3",
            ),
            css_class="px-3",
        )
    )
