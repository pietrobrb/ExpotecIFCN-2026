from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset
from django.urls import reverse_lazy
from extra_views import InlineFormSetFactory

from django.utils.translation import gettext_lazy as _
from core.forms import DateInput, Select2Widget
from documentos.models import Documento, TipoDocumento
from enderecos.forms import  EnderecoForm
from enderecos.models import Contato
from usuarios.models import User, Vinculos
from .models import AreaTematica, Avaliador, Comissao, Evento, EventoContato, EventoDocumento, ItemGaleria, Membro, Monitor, Noticia, Parceiro
from betterforms.multiform import MultiModelForm
from django_summernote.widgets import SummernoteWidget    
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'titulo', 
            'subtitulo', 
            'edicao', 
            'ano', 
            'dt_inicio', 
            'dt_encerramento', 
            'apresentacao', 
            'instagram', 
            'youtube', 
            'logo', 
            'logo_mini', 
            'imagem_promocional', 
            'video_promocional', 
            'ch_total'
        ]
        widgets = { 'dt_inicio': DateInput(),
                    'dt_encerramento': DateInput(),
                    'ano': forms.TextInput(attrs={'type': 'number', 'min': '1'}), 
                    'apresentacao': SummernoteWidget(),
                    'logo': forms.FileInput(attrs={'accept': 'image/*'}),
                    'logo_mini': forms.FileInput(attrs={'accept': 'image/*'}),
                    'imagem_promocional': forms.FileInput(attrs={'accept': 'image/*'}),
                    'video_promocional': forms.FileInput(attrs={'accept': 'video/*'}),
                }
        
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("titulo", css_class="col-md-4"),
                Column("subtitulo", css_class="col-md-8"),
                Column("edicao", css_class="col-md-2"),
                Column("ano", css_class="col-md-2"),
                Column("dt_inicio", css_class="col-md-3"),
                Column("dt_encerramento", css_class="col-md-3"),
                Column("ch_total", css_class="col-md-2"),
            
                Column("instagram", css_class="col-md-6"),
                Column("youtube", css_class="col-md-6"),
                 
                Column("logo", css_class="col-md-6"),
                Column("logo_mini", css_class="col-md-6"),

                Column("imagem_promocional", css_class="col-md-6"),
                Column("video_promocional", css_class="col-md-6"),

                Column("apresentacao", css_class="col-md-12"),
            ),
        )
    )


class EventoComissaoForm(forms.ModelForm):
    class Meta:
        model = Comissao
        fields = ['nome']

class EventoParceiroForm(forms.ModelForm):
    class Meta:
        model = Parceiro
        fields = ['nome', 'logo', 'url']
        widgets = {
            'logo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("nome", css_class="col-md-4"),
                Column("url", css_class="col-md-8"),
                Column("logo", css_class="col-md-12"),
            ),
        )
    )
class EventoItemGaleriaForm(forms.ModelForm):
    class Meta:
        model = ItemGaleria
        fields = ['titulo', 'img', 'url']
        widgets = {
            'img': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("titulo", css_class="col-md-4"),
                Column("url", css_class="col-md-8"),
                Column("img", css_class="col-md-12"),
            ),
        )
    )

class EventoNoticiaForm(forms.ModelForm):
    
    class Meta:
        model = Noticia
        fields = ['titulo', 'subtitulo', 'poster', 'thumbnail', 'texto', 'ordem', 'url']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3}),
            'poster': forms.FileInput(attrs={'accept': 'image/*'}),
            'thumbnail': forms.FileInput(attrs={'accept': 'image/*'}),
            'url': forms.TextInput(attrs={'type': 'url'}),
        }

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("titulo", css_class="col-md-12"),
                Column("subtitulo", css_class="col-md-6"),
                Column("url", css_class="col-md-4"),
                Column("ordem", css_class="col-md-2"),
                Column("poster", css_class="col-md-6"),
                Column("thumbnail", css_class="col-md-6"),
                Column("texto", css_class="col-md-12"),
            ),
        )
    )
class EventoDocumentoForm(forms.ModelForm):
    documento_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    descricao = forms.CharField(max_length=255, required=True, label="Descrição")
    tipo = forms.ChoiceField(choices=TipoDocumento.choices, required=True, widget=Select2Widget(attrs={"data-placeholder": "----"}))
    file = forms.FileField(required=True, label="Arquivo")

    class Meta:
        model = EventoDocumento
        fields = ['documento_id', 'descricao', 'tipo', 'file']
        widgets = {
            
        }
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("descricao", css_class="col-md-8"),
                Column("tipo", css_class="col-md-4"),
                Column("file", css_class="col-md-12"),
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


class EventoAreaTematicaForm(forms.ModelForm):
    class Meta:
        model = AreaTematica
        fields = ['nome', 'descricao', 'cor', 'icone']
        widgets = {
            'cor': forms.TextInput(attrs={'type': 'color'}),
            'descricao': SummernoteWidget(),
        }

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("nome", css_class="col-md-6"),
                Column("cor", css_class="col-md-3"),
                Column("icone", css_class="col-md-3"),
                Column("descricao", css_class="col-md-12"),
            ),
        )
    )


class EventoContatoForm(forms.ModelForm):
    nome = forms.CharField(label="Nome", max_length=100, required=True)
    email = forms.EmailField(label="Email", required=False)
    telefone = forms.CharField(label="Telefone", max_length=20, required=False)

    class Meta:
        model = EventoContato
        fields = ['nome', 'email', 'telefone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.contato:
            contato = self.instance.contato
            self.fields['nome'].initial = contato.nome
            self.fields['email'].initial = contato.email
            self.fields['telefone'].initial = contato.telefone

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("nome", css_class="col-md-6"),
                Column("email", css_class="col-md-3"),
                Column("telefone", css_class="col-md-3"),
            ),
        )
    )

    def save(self, commit=True):
        contato, created = Contato.objects.get_or_create(
            nome=self.cleaned_data['nome'],
            email=self.cleaned_data['email'],
            telefone=self.cleaned_data['telefone']
        )
        evento_contato = super().save(commit=False)
        evento_contato.contato = contato
        if commit:
            evento_contato.save()
        return evento_contato

class EventoContatoInline(InlineFormSetFactory):
    model = EventoContato
    form_class = EventoContatoForm
    factory_kwargs = dict(extra=0, can_delete=True, fk_name="evento")

class EventoEnderecoMultiForm(MultiModelForm):
    form_classes = {
        'evento': EventoForm,
        'endereco': EnderecoForm,
    }
    
    def __init__(self, *args, **kwargs):
        # join all models
        instance = kwargs.pop("instance", None)
        if instance is not None:
            kwargs["instance"] = {
                "pk":instance.pk,
                "evento": instance,
                "endereco": instance.endereco,
            }
        super().__init__(*args, **kwargs)


class EventoMembroComissaoForm(forms.ModelForm):
    nome_completo = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(
            attrs={'class': 'form-control select_user',
                'onchange': 'getUserData(this);',
            })
        )
    vinculo = forms.ChoiceField(choices=Vinculos.choices, required=True, widget=Select2Widget(attrs={'data-placeholder': '----'}))
    usuario = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=forms.HiddenInput())

    class Meta:
        model = Membro
        fields = ['email', 'nome_completo', 'vinculo', 'presidente', 'usuario']
        widgets = {
            'presidente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        


    def __init__(self, membro=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        if self.instance.pk and self.instance.usuario and self.instance.usuario.pk:
            user = self.instance.usuario
            self.fields['nome_completo'].initial = user.nome_completo
            self.fields['email'].initial = user.email
            self.fields['vinculo'].initial = user.vinculo
            self.fields['presidente'].initial = self.instance.presidente
            readonly_fields = [ 'nome_completo', 'vinculo']
            for field in readonly_fields:
                if field in self.fields:
                    self.fields[field].widget.attrs['readonly'] = True
        
        
    
    # Configure Crispy Forms helper
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("usuario", css_class="col-md-12"),
            ),
            Row(
                Column("email", css_class="col-md-6"),
                Column("vinculo", css_class="col-md-4"),
                Column("presidente", css_class="col-md-2 pt-3 d-flex align-items-center justify-content-center"),
                Column("nome_completo", css_class="col-md-12"),
                
                
            )   
        )
    )

    
class EventoMembroComissaoInline(InlineFormSetFactory):
    model = Membro
    form_class = EventoMembroComissaoForm
    factory_kwargs = dict(extra=0, can_delete=True, fk_name="comissao")


class MonitorForm(forms.ModelForm):
    nome = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control','readonly': 'readonly'}))
    matricula = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    curso = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))    
    confirmacao = forms.BooleanField(
        label=_("Confirmo que estou ciente que, ao me inscrever como monitor, estou apto a dar suporte a qualquer atividade do evento."),
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = Monitor
        fields = ['ira', 'ano', 'descricao', 'confirmacao']
        widgets = {
            'ira': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['nome'].initial = usuario.nome_completo
            self.fields['matricula'].initial = usuario.matricula
            self.fields['curso'].initial = usuario.curso

        if self.instance and self.instance.pk:
            self.fields['confirmacao'].initial = True
            
       
    def clean_confirmacao(self):
        confirmacao = self.cleaned_data.get('confirmacao')
        
        if not confirmacao:
            raise forms.ValidationError("Você deve confirmar que está ciente das normas para se inscrever como monitor.")

        return confirmacao
    
    helper = FormHelper()
    helper.layout = Layout(
            Row(
                Column("matricula", css_class="col-md-4"),
                Column("nome", css_class="col-md-8"),
                Column("curso", css_class="col-md-4 "),
                Column("ano", css_class="col-md-4"),
                Column("ira", css_class="col-md-4 "),
                Column("descricao", css_class="col-md-12 "),
                Column("confirmacao", css_class="col-md-12 pt-3 border-top"), css_class="px-3"
            ),
    )