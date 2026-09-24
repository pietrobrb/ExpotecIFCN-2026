from core.forms import Select2Widget
from documentos.models import TipoDocumento
from .models import AreaTematica, Avaliador, Comissao, EventoDocumento, ItemGaleria, Noticia, Parceiro
from django_filters import filters
from django_filters.filterset import FilterSet
from django import forms

class EventoDocumentoFilter(FilterSet):
    documento_descricao = filters.CharFilter(
        field_name='documento__descricao', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Descrição do documento"}
        )
    )
    documento_tipo = filters.ChoiceFilter(
        field_name='documento__tipo', 
        choices=TipoDocumento.choices, 
        label=None,                                         
        widget=forms.Select(
            attrs={"class": "form-select","data-placeholder": "Tipo"}
        ),
        
        empty_label="Tipo"
    )

    class Meta:
        model = EventoDocumento
        fields = ['documento_descricao', 'documento_tipo']

class ComissaoFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='nome', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Nome"}
        )
    )
    class Meta:
        model = Comissao
        fields = ['nome']



class AreaTematicaFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='nome', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Nome"}
        )
    )
    class Meta:
        model = AreaTematica
        fields = ['nome']

class ParceiroFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='nome', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Nome"}
        )
    )
    class Meta:
        model = Parceiro
        fields = ['nome']

class ItemGaleriaFilter(FilterSet):
    nome = filters.CharFilter(
        field_name='titulo', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Título"}
        )
    )
    class Meta:
        model = ItemGaleria
        fields = ['nome']

class NoticiaFilter(FilterSet):
    titulo = filters.CharFilter(
        field_name='titulo', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput(  # Corrigido para forms.TextInput
            attrs={"class": "form-control", "placeholder": "Nome"}
        )
    )
    class Meta:
        model = Noticia
        fields = ['titulo']

class AvaliadorFilter(FilterSet):
    email = filters.CharFilter(
        field_name='usuario__email', 
        lookup_expr='icontains', 
        label="", 
        widget=forms.TextInput( 
            attrs={"class": "form-control", "placeholder": "Digite o email"}
        )
    )

    area = filters.ModelChoiceFilter(  
        queryset=AreaTematica.objects.all(), 
        field_name = "areas_tematicas",
        label=None,
        widget=forms.Select(
            attrs={"class": "form-select", "data-placeholder": "Área"}
        ),
        empty_label="Área"
    )

    class Meta:
        model = Avaliador
        fields = ['email','area']