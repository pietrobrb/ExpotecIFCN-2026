
from django import forms
from pydantic import ValidationError
from atividades.models import Atividade, InscricaoAtividade, TipoAtividade
from core.forms import ModelSelect2Widget, Select2Widget
from eventos.models import InscricaoEvento
from usuarios.models import User, Vinculos
from django_filters.filterset import FilterSet
from django_filters import filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column

class InscricaoEventoFilter(FilterSet):
    email = filters.CharFilter(
        field_name='usuario__email', 
        lookup_expr='icontains', 
        label="Email do usuário", 
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite o email do usuário"}
        ),

    )
    vinculo = filters.ChoiceFilter(
        field_name='usuario__vinculo', 
        choices=Vinculos.choices, 
        label="Vínculo do usuário",                                         
        widget=forms.Select(
            attrs={"class": "form-select","data-placeholder": "Vículo do usuário"}
        ),
        
    )

    class Meta:
        model = InscricaoEvento
        fields = ['email', 'vinculo']

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("usuario__email", css_class="col-md-4"),
            ),
        )
    )




class InscricaoAtividadeFilter(FilterSet):
    email = filters.CharFilter(
        field_name='usuario__email',
        lookup_expr='icontains',
        label="Email do usuário",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Email do usuário"})
    )
    atividade = filters.ModelChoiceFilter(
        queryset=Atividade.objects.all(),
        label="Atividade",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    tipo = filters.ModelChoiceFilter(
        queryset=TipoAtividade.objects.all(),
        label="Tipo de Atividade",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = InscricaoAtividade
        fields = ['email', 'atividade', 'tipo']

    helper = FormHelper()
    helper.layout = Layout(
            Fieldset(
                "",
                Row(
                    Column("email", css_class="col-md-4"),
                ),
                Row(
                    Column("atividade", css_class="col-md-4"),
                ),
                Row(
                    Column("tipo", css_class="col-md-4"),
                ),
            )
        )


class InscricaoAtividadeForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email do usuário",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Digite o email do usuário"})
    )

    class Meta:
        model = InscricaoAtividade
        fields = ['email', 'atividade', 'presente']
        widgets = {
            'atividade': forms.Select(attrs={"class": "form-select"}),
            'presente': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            'atividade': 'Atividade',
            'presente': 'Presente'
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        atividade = cleaned_data.get('atividade')

        try:
            usuario = User.objects.get(email=email)
            cleaned_data['usuario'] = usuario
        except User.DoesNotExist:
            self.add_error('email', "Usuário com este email não foi encontrado.")
            return cleaned_data

    
        if atividade and InscricaoAtividade.objects.filter(usuario=usuario, atividade=atividade).exists():
            self.add_error('atividade', "O usuário informado já está inscrito na atividade selecionada.")

        return cleaned_data