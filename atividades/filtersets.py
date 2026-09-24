from django_filters import filters
from django_filters.filterset import FilterSet
from django import forms

from core.forms import ModelSelect2Widget, Select2Widget
from .models import Agendamento, Sala, StatusAtividade, TipoAtividade, Atividade
from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ChoiceFilter
from django import forms
from django_select2 import forms as s2forms
class AtividadeFilter(FilterSet):
    titulo = CharFilter(
        field_name='titulo', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(
            
            attrs={"class": "form-control", "placeholder": "Título"}
        )
    )
    tipo = ModelChoiceFilter(  # Corrigido para ModelChoiceFilter
        queryset=TipoAtividade.objects.all(), 
        label=None,
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Tipo"}
        ),
        empty_label="Tipo"
    )
    status = ChoiceFilter(
        choices=StatusAtividade.choices, 
        label="",                                         
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Status"}
        ),
        empty_label="Status"
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        if request and hasattr(request, 'evento') and request.evento:
            self.filters['tipo'].queryset = TipoAtividade.objects.filter(evento=request.evento)


    class Meta:
        model = Atividade
        fields = ['titulo', 'tipo', 'status'] 

    
class AtividadeInscricaoFilter(FilterSet):
    titulo = CharFilter(
        field_name='titulo', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(
            
            attrs={"class": "form-control", "placeholder": "Título"}
        )
    )
    tipo = ModelChoiceFilter(  # Corrigido para ModelChoiceFilter
        queryset=TipoAtividade.objects.all(), 
        label=None,
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Tipo"}
        ),
        empty_label="Tipo"
    )
    
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        if request and hasattr(request, 'evento') and request.evento:
            self.filters['tipo'].queryset = TipoAtividade.objects.filter(evento=request.evento)


    class Meta:
        model = Atividade
        fields = ['titulo', 'tipo'] 


class TipoAtividadeFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='nome', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Nome"}
        )
    )
    class Meta:
        model = TipoAtividade
        fields = ['nome']

class SalaFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='nome', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Nome"}
        )
    )
    class Meta:
        model = Sala
        fields = ['nome']

class AgendamentoFilter(FilterSet):
    tipo = ModelChoiceFilter(
        queryset=TipoAtividade.objects.all(),
        field_name='atividade__tipo',
        label=None,
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Tipo de atividade"}
        ),
        empty_label="Tipo de Atividade"
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        if request and hasattr(request, 'evento') and request.evento:
            self.filters['tipo'].queryset = TipoAtividade.objects.filter(evento=request.evento)
    class Meta:
        model = Agendamento
        fields = ['tipo'] 