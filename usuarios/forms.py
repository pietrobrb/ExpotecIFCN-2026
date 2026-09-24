from django import forms
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import (
    SignupForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
)
from betterforms.multiform import MultiModelForm
from core.forms import ModelSelect2MultipleWidget
from enderecos.forms import EnderecoForm
from eventos.models import AreaTematica, Avaliador, InscricaoEvento
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset
from .models import User, Vinculos
import re


class UserSignupForm(SignupForm):
    nome_completo = forms.CharField(
        max_length=100,
        label="Nome Completo",
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Nome Completo'}
        ),
    )
    vinculo = forms.ChoiceField(
        choices=[
            (member.value, member.label) for member in [
                Vinculos.ESTUDANTE,
                Vinculos.PROFISSIONAL,
                Vinculos.OUTRO,
                ]
            ],
        label="Vínculo",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, request):
        user = super(UserSignupForm, self).save(request)

        user.nome_completo = self.cleaned_data['nome_completo']
        user.vinculo = self.cleaned_data['vinculo']

        user.save()
        return user


class UserLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class UserResetPasswordForm(ResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class UserResetPasswordKeyForm(ResetPasswordKeyForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class InscricaoEventoForm(forms.ModelForm):
    
    class Meta:
        model = InscricaoEvento
        fields = []

class PerfilForm(forms.ModelForm):
    cpf = forms.CharField(
        label="CPF",
        max_length=11,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'CPF'}
        ),
        required=True
    )
    foto_perfil = forms.ImageField(
        label="Foto de Perfil",
        widget=forms.FileInput(
            attrs={'class': 'form-control'}
        ),
        required=True
    )

    def clean_cpf(self):
        cpf = re.sub(r'[^0-9]', '', self.cleaned_data["cpf"])
        if len(cpf) != 11:
            raise forms.ValidationError("CPF deve conter 11 dígitos.")
        if cpf == cpf[0] * len(cpf):
            raise forms.ValidationError("CPF inválido.")
        for i in range(9, 11):
            soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(0, i))
            digito = (soma * 10 % 11) % 10
            if digito != int(cpf[i]):
                raise forms.ValidationError("CPF inválido.")
        return(cpf)
        

    class Meta:
        model = User
        fields = ['nome_completo','cpf', 'vinculo', 'foto_perfil', 'instituicao', 'matricula', 'campus', 'curso']
        required_fields = ['cpf', 'foto_perfil']
        widgets = {
            'vinculo': forms.TextInput(attrs={'class': 'form-control', 'readonly':'True'}),
        }
        

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
            )
        )
    )
    
class InscricaoEventoMuiltForm(MultiModelForm):
    form_classes = {
        'usuario': PerfilForm,
        'endereco': EnderecoForm,
        'inscricao' : InscricaoEventoForm
    }
    
    def __init__(self, *args, **kwargs):
        # join all models
        instance = kwargs.pop("instance", None)
        if instance is not None:
            kwargs["instance"] = {
                "pk":instance.pk,
                "usuario": instance.usuario,
                "endereco": instance.usuario.endereco,
            }
        super().__init__(*args, **kwargs)
        self.forms['endereco'].fields['local'].widget = forms.HiddenInput()

class MeuPerfilMuiltForm(MultiModelForm):
    form_classes = {
        'usuario': PerfilForm,
        'endereco': EnderecoForm
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.forms['endereco'].fields['local'].widget = forms.HiddenInput()


class EventoAvaliadorForm(forms.ModelForm):
    areas_tematicas = forms.ModelMultipleChoiceField(
        required=True,
        label="",
        queryset=AreaTematica.objects.all().order_by("nome"),
        widget=forms.CheckboxSelectMultiple()
    )

    confirmacao = forms.BooleanField(
        label=_("Confirmo que estou ciente que, ao me inscrever como avaliador, estou apto a avaliar qualquer trabalho das áreas temáticas selecionadas."),
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = Avaliador
        fields = ['areas_tematicas', 'confirmacao']

    def __init__(self, *args, **kwargs):
        super(EventoAvaliadorForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.areas_tematicas.exists():
            self.fields['confirmacao'].initial = True
       
    def clean_confirmacao(self):
        confirmacao = self.cleaned_data.get('confirmacao')
        
        if not confirmacao:
            raise forms.ValidationError("Você deve confirmar que está ciente das normas para se inscrever como avaliador.")

        return confirmacao
    helper = FormHelper()
    helper.layout = Layout(
            Row(
                Column("areas_tematicas", css_class="col-md-12 border-bottom"),
                Column("confirmacao", css_class="col-md-12 mt-3"), css_class="px-3"
            ),
    )


