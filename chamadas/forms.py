from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, Field
from extra_views import InlineFormSetFactory
from chamadas.models import OpcoesChamada, TipoChamada, TipoChamadaDocumento, CriterioAvaliacao, Chamada, StatusChamada, FormaAvaliacao
from core.forms import DateInput, Select2Widget
from datetime import date
from django.utils.translation import gettext_lazy as _
from documentos.forms import DocumentoForm
from documentos.models import Documento, TipoDocumento
from django_summernote.widgets import SummernoteWidget  


class TipoChamadaForm(forms.ModelForm):
    class Meta:
        model = TipoChamada
        fields = [
            'nome', 
            'descricao', 
            'max_autores',
            'opcoes'
        ]
        widgets = { 
            'descricao': SummernoteWidget(),
            'opcoes': forms.CheckboxSelectMultiple(choices=OpcoesChamada.choices, attrs={'class': 'form-check-input '}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    helper = FormHelper()
    helper.layout = Layout(
            Row(
                Column("nome", css_class="col-md-9"),
                Column("max_autores", css_class="col-md-3"),
                Column("descricao", css_class="col-md-12"),
                Field("opcoes", template="widgets/custom_checkbox_select_multiple.html", css_class="d-flex flex-column flex-md-row flex-wrap"), 
                
            ),
       
    )
    

class TipoChamadaDocumentForm(DocumentoForm):
    documento_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    descricao = forms.CharField(max_length=255, required=True, label="Descrição")
    tipo = forms.ChoiceField(choices=[(TipoDocumento.REGRA, _("Regra")),(TipoDocumento.MODELO,_('Modelo'))], required=True, widget=Select2Widget(attrs={"data-placeholder": "----"}))
    file = forms.FileField(required=True, label="Arquivo")

    class Meta:
        model = TipoChamadaDocumento
        fields = ['documento_id', 'descricao', 'tipo', 'file']
        widgets = {
            
        }
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("descricao", css_class="col-md-4"),
                Column("tipo", css_class="col-md-2"),
                Column("file", css_class="col-md-6"),
            ),
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        documento_id = cleaned_data.get('documento_id')
        descricao = cleaned_data.get('descricao')
        if descricao is None:
            return cleaned_data
        
        tipo = cleaned_data.get('tipo')
        if tipo is None:
            return cleaned_data

        file = cleaned_data.get('file')
        if file is None:
            return cleaned_data

        documento = Documento.objects.get(id=documento_id) if documento_id else None
        if documento:
            documento.descricao = descricao
            documento.tipo = tipo
            if file:
                documento.file = file
            documento.save()
        else:
            documento = Documento.objects.create(
                descricao=descricao,
                tipo=tipo,
                file=file
            )

        cleaned_data['documento_id'] = documento.id
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.documento:
            self.fields['documento_id'].initial = self.instance.documento.id
            self.fields['descricao'].initial = self.instance.documento.descricao
            self.fields['tipo'].initial = self.instance.documento.tipo
            self.fields['file'].initial = self.instance.documento.file

                

    def save(self, commit=True):
        instance = super().save(commit=False)
        documento_id = self.cleaned_data.get('documento_id')
        documento = Documento.objects.get(id=documento_id)
        instance.documento = documento
        if commit:
            if instance.documento.descricao:
                instance.save()
        return instance

class TipoChamadaDocumentoInline(InlineFormSetFactory):
    model = TipoChamadaDocumento
    form_class = TipoChamadaDocumentForm
    factory_kwargs = dict(extra=0, can_delete=True, fk_name="tipo_chamada")

from datetime import date
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column

class ChamadaForm(forms.ModelForm):
    tem_submissao = forms.TypedChoiceField(
        choices=((True, 'Sim'), (False, 'Não')),
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = Chamada
        fields = ['tipo', 'dt_inicio', 'dt_encerramento', 'etapa', 'tem_submissao', 'forma_avaliacao', 'status', 'min_avaliacoes']
        widgets = {
            'dt_inicio': DateInput(),
            'dt_encerramento': DateInput(),
            'etapa': Select2Widget(),
            'status': Select2Widget(),
            'tipo': Select2Widget(),
            'forma_avaliacao': Select2Widget(),
            'min_avaliacoes': forms.TextInput(attrs={'type': 'number', 'min': '0', 'max': '5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "",
                Row(
                    Column("tipo", css_class="col-md-3"),
                    Column("etapa", css_class="col-md-3"),
                    Column("dt_inicio", css_class="col-md-3"),
                    Column("dt_encerramento", css_class="col-md-3"),
                    Column("status", css_class="col-md-3"),
                    Column("tem_submissao", css_class="col-md-3"),
                    Column("forma_avaliacao", css_class="col-md-3"),
                    Column("min_avaliacoes", css_class="col-md-3"),
                ),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        dt_inicio = cleaned_data.get('dt_inicio')
        dt_encerramento = cleaned_data.get('dt_encerramento')
        etapa = cleaned_data.get('etapa')
        forma_avaliacao = cleaned_data.get('forma_avaliacao')
        min_avaliacoes = cleaned_data.get('min_avaliacoes')
        
        """if not dt_inicio:
            self.add_error('dt_inicio', 'A data de início é obrigatória.')
        if not dt_encerramento:
            self.add_error('dt_encerramento', 'A data de encerramento é obrigatória.')
        if not etapa:
            self.add_error('etapa', 'A etapa é obrigatória.')
        """
        if forma_avaliacao != FormaAvaliacao.SEM and (min_avaliacoes is None or min_avaliacoes <= 0):
            self.add_error('min_avaliacoes', 'Mínimo de avaliações deve ser superior a 0.')

        # Validação das datas
        if dt_inicio and dt_encerramento and dt_inicio > dt_encerramento:
            self.add_error('dt_encerramento', 'A data de encerramento deve ser posterior à data de início.')
                
        return cleaned_data



class ChamadaCriterioForm(forms.ModelForm):
    class Meta:
        model = CriterioAvaliacao
        fields = ['nome', 'descricao', 'peso']
        widgets = {
            'peso': forms.TextInput(attrs={'type': 'number', 'min': '1', 'max':'100'}),
        }    
    
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("nome", css_class="col-md-3"),
                Column("descricao", css_class="col-md-6"),
                Column("peso", css_class="col-md-3 peso_container"),
            ),
        )
    )


    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        peso = cleaned_data.get('peso')

        if not nome:
            self.add_error('nome', 'O nome é obrigatório.')
        if not peso:
            self.add_error('peso', 'O peso é obrigatório.')
        
        return cleaned_data
    
class ChamadaCriterioInline(InlineFormSetFactory):
    model = CriterioAvaliacao
    form_class = ChamadaCriterioForm
    factory_kwargs = dict(extra=0, can_delete=True, fk_name="chamada")
