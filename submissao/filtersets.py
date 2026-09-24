from django_filters import filters
from django_filters.filterset import FilterSet
from django import forms

from chamadas.models import EtapaChamada, TipoChamada
from .models import AreaTematica, StatusAvaliacao, StatusTrabalho, Trabalho, User
from core.forms import Select2Widget
from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ChoiceFilter

class SubmissaoFilter(FilterSet):
    titulo= filters.CharFilter(
        field_name='trabalho__titulo', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput( 
            attrs={"class": "form-control", "placeholder": "Digite o título do Trabalho"}
        )
    )

    status = ChoiceFilter(
        field_name="trabalho__status",
        choices=StatusTrabalho.choices, 
        label="",                                         
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Status"}
        ),
        empty_label="Status"
    )

    tipo_chamada = ModelChoiceFilter(  # Corrigido para ModelChoiceFilter
        queryset=TipoChamada.objects.all(), 
        field_name = "chamada__tipo",
        label=None,
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Área"}
        ),
        empty_label="Tipo"
    )

    etapa = ChoiceFilter(
        field_name="chamada__etapa",
        choices=EtapaChamada.choices, 
        label="",                                         
        widget=forms.HiddenInput(
            attrs={"class": "form-select", "data-placeholder": "Chamada"}
        ),
        empty_label="Etapa"
    )
    
    area = ModelChoiceFilter(  # Corrigido para ModelChoiceFilter
        queryset=AreaTematica.objects.all(), 
        field_name = "trabalho__area_tematica",
        label=None,
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Área"}
        ),
        empty_label="Área"
    )

    class Meta:
        model = Trabalho
        fields = ['titulo', 'status', 'tipo_chamada',  'etapa','area',]