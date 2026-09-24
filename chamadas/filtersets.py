
from .models import TipoChamada, Chamada, StatusChamada, EtapaChamada
from django_filters import filters
from django_filters.filterset import FilterSet
from django import forms

class TipoChamadaFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='nome', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Nome da chamada"}
        )
    )
    class Meta:
        model = TipoChamada
        fields = ['nome']

class ChamadaFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='tipo__nome', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Descrição da chamada"}
        )
    )
    etapa = filters.ChoiceFilter(
        field_name='etapa', 
        choices=EtapaChamada.choices, 
        label="",                                         
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "etapa"}
        ),
        empty_label="Etapa"
    )
    status = filters.ChoiceFilter(
        field_name='status', 
        choices=StatusChamada.choices, 
        label="",                                         
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Status"}
        ),
        empty_label="Status"
    )

    class Meta:
        model = Chamada
        fields = ['nome','etapa', 'status']