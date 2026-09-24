from django import forms
from .models import Contato, Endereco, Estado, Cidade
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset
from core.forms import Select2Widget, ModelSelect2Widget

class EstadoWidget(ModelSelect2Widget):
    model = Estado
    search_fields = ['nome__istartswith', 'sigla__icontains']
    default = "Rio Grande do Norte"


class CidadeWidget(ModelSelect2Widget):
    model = Cidade
    dependent_fields = {'estado': 'estado'}
    search_fields = ['nome__istartswith']


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['pais', 'estado', 'cidade', 'logradouro', 'local']
        widgets = {
            'estado': EstadoWidget,
            'cidade': CidadeWidget,
        }

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("pais", css_class="col-md-4"),
                Column("estado", css_class="col-md-4"),
                Column("cidade", css_class="col-md-4"),
                Column("logradouro", css_class="col-md-8"),
                Column("local", css_class="col-md-4"),
            ),
        )
    )
        

class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'email', 'telefone']
        labels = {
            'nome': 'Nome',
            'email': 'Email',
            'telefone': 'Telefone',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'type': 'email'}),
        }

