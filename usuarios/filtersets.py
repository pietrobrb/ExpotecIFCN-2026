from django_filters import filters, FilterSet
from django import forms

from atividades.models import InscricaoAtividade, TipoAtividade
from eventos.models import Evento

class InscricaoAtividadeFilter(FilterSet):
    tipo = filters.ModelChoiceFilter(  # Corrigido para ModelChoiceFilter
        field_name='atividade__tipo', 
        queryset=TipoAtividade.objects.all(),
        label="",                                         
        widget=forms.Select(
            attrs={"class": "form-control pr-5", "data-placeholder": "Tipo"}
        ),
        empty_label="Tipo"
    )

    atividade = filters.CharFilter(
        field_name='atividade__titulo', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Título da Atividade"}
        )
    )
    
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        if request and hasattr(request, 'evento') and request.evento:
            self.filters['tipo'].queryset = TipoAtividade.objects.filter(evento=request.evento)
    class Meta:
        model = InscricaoAtividade
        fields = ['atividade', 'tipo']
