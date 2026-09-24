from ast import Div
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset,HTML
from django.urls import reverse_lazy
from pydantic import ValidationError
from documentos.models import Documento
from .models import Avaliacao, AvaliacaoCriterio, CriterioAvaliacao, StatusAvaliacao, StatusTrabalho, Submissao, Trabalho, User
from chamadas.models import Chamada, EtapaChamada, FormaAvaliacao, OpcoesChamada, StatusChamada, TipoChamada
from eventos.models import AreaTematica, Avaliador
from eventos.models import TipoDocumento
from extra_views import InlineFormSetFactory
from core.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from betterforms.multiform import MultiModelForm
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Trabalho, TipoChamada, AreaTematica, User
from django.utils.text import slugify

class MeuTrabalhoForm(forms.ModelForm):
    resumo = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label="Resumo*", required=False)
    palavras_chave = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Palavras-chave separadas por vírgula'}), label="Palavras-chave*", required=False)
    descricao = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label="Descrição*", required=False)
    
    class Meta:
        model = Trabalho
        fields = ['titulo', 'area_tematica', 'resumo', 'palavras_chave', 'descricao', 'autor_principal', 'coautores', 'tipo_chamada']
        widgets = {
            'tipo_chamada': forms.Select(
                attrs={
                    'class': 'form-control',
                    "hx-trigger": "change",
                    "hx-get": reverse_lazy("user:trabalho-get_campos_opcionais"),
                    "hx-target": "#add_on",
                },
            ),
            'area_tematica': ModelSelect2Widget(
                model=AreaTematica,
                required=True,
                search_fields=['nome__icontains'],
                attrs={'class': 'form-control', 'data-minimum-input-length': 0},
            ),
            'autor_principal': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'coautores': ModelSelect2MultipleWidget(
                model=User,
                search_fields=['email__icontains'],
                attrs={'class': 'form-control'},
            ),
        }

    def __init__(self, *args, **kwargs):
        self.evento = kwargs.pop('evento', None)
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if self.evento:
            self.fields['tipo_chamada'].queryset = TipoChamada.objects.filter(chamadas__etapa=EtapaChamada.INICIAL, evento=self.evento)
            self.fields['coautores'].queryset = User.objects.all()
            self.fields['autor_principal'].initial = self.usuario

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "",
                Row(
                    Column("tipo_chamada", css_class="col-md-6"),
                    Column("area_tematica", css_class="col-md-6"),
                    Column("titulo", css_class="col-md-8"),
                    Column("autor_principal", css_class="col-md-4"),
                    Column("coautores", css_class="col-md-12"),
                    HTML("<div id='add_on' class='px-2'></div>"),
                ),
            )
        )
        
        if self.instance.pk and hasattr(self.instance, 'tipo_chamada'):
            self.fields['tipo_chamada'].widget.attrs['readonly'] = 'readonly'
            self.configure_optional_fields()

    def configure_optional_fields(self):
        if OpcoesChamada.RESUMO in self.instance.tipo_chamada.opcoes:
            self.helper.layout[0].append(Column('resumo', css_class='col-md-12 px-0'))
            self.helper.layout[0].append(Column('palavras_chave', css_class='col-md-12 px-0'))
        
        if OpcoesChamada.DESCRICAO in self.instance.tipo_chamada.opcoes:
            self.helper.layout[0].append(Column('descricao', css_class='col-md-12 px-0'))

    def clean_autor_principal(self):
        autor_principal = self.cleaned_data.get('autor_principal')
        if autor_principal:
            trabalhos = Trabalho.objects.filter(autor_principal=autor_principal).exclude(pk=self.instance.pk)
            if trabalhos.count() >= 2:
                raise forms.ValidationError(f'O autor principal já possui {trabalhos.count()} trabalhos cadastrados.')
        return autor_principal

    def clean(self):
        cleaned_data = super().clean()
        tipo_chamada = cleaned_data.get('tipo_chamada')
        coautores = cleaned_data.get('coautores')
        autor_principal = cleaned_data.get('autor_principal')
        self.validate_autores(autor_principal, coautores, tipo_chamada)
        self.validate_titulo_unico(cleaned_data.get("titulo"))
        self.validate_campos_opcionais(tipo_chamada)
        return cleaned_data

    def validate_autores(self, autor_principal, coautores, tipo_chamada):
        if autor_principal in coautores.all():
            self.add_error('coautores', "Autor principal não pode estar em coautores")
        
        total_autores = 1 + coautores.count() 
        if tipo_chamada and total_autores > tipo_chamada.max_autores:
            self.add_error('coautores', f"Número total de autores excede o máximo permitido ({tipo_chamada.max_autores}).")
        
        if self.usuario and not (autor_principal == self.usuario or coautores.filter(id=self.usuario.id).exists()):
            self.add_error('coautores', "Você deve estar listado como autor principal ou coautor deste trabalho.")

    def validate_titulo_unico(self, titulo):
        if Trabalho.objects.filter(slug=slugify(titulo)).exclude(pk=self.instance.pk).exists():
            self.add_error('titulo', "Título já cadastrado")

    def validate_campos_opcionais(self, tipo_chamada):
        if tipo_chamada:
            print(tipo_chamada.opcoes)
            if OpcoesChamada.RESUMO in tipo_chamada.opcoes and not self.cleaned_data.get('resumo'):
                self.add_error('resumo', 'Resumo é obrigatório para esta chamada.')
                raise forms.ValidationError("Resumo e palavras chave são obrigatórios para esta chamada.")
            if OpcoesChamada.RESUMO in tipo_chamada.opcoes and not self.cleaned_data.get('palavras_chave'):
                self.add_error('palavras_chave', 'Palavras-chaves são obrigatórias para esta chamada.')    
                raise forms.ValidationError("Palavras-chaves são obrigatórias para esta chamada.")
            if OpcoesChamada.DESCRICAO in tipo_chamada.opcoes and not self.cleaned_data.get('descricao'):
                self.add_error('descricao', 'Descrição é obrigatória para esta chamada.')
                raise forms.ValidationError("Descrição é obrigatória para esta chamada.")


class MeuTrabalhoAutoSubmissaoForm(MeuTrabalhoForm):
    documento_identificado = forms.FileField(
        required=False, 
        label="Documento identificado (ex: *.doc, *.docx)", 
        widget=forms.ClearableFileInput(attrs={'accept': '.doc,.docx'})
    )
    documento_n_identificado = forms.FileField(
        required=False, 
        label="Documento não identificado (ex: *.pdf)", 
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf'})
    )

    ciencia = forms.BooleanField(required=True, label="Declaro que estou ciente de todas as informações contidas nas orientações da chamada e que as informações declaradas por mim neste formulário são de minha inteira responsabilidade.")
    

    class Meta(MeuTrabalhoForm.Meta):
        fields = MeuTrabalhoForm.Meta.fields + ['documento_identificado', 'documento_n_identificado', 'ciencia']
        widgets = {
            'tipo_chamada': forms.Select(
                attrs={
                    'class': 'form-control',
                    "hx-trigger": "load, change",
                    "hx-get": reverse_lazy("user:trabalho-get_campos_opcionais"),
                    "hx-target": "#add_on",
                },
            ),
            'area_tematica': ModelSelect2Widget(
                model=AreaTematica,
                required=True,
                search_fields=['nome__icontains'],
                attrs={'class': 'form-control', 'data-minimum-input-length': 0},
            ),
            'autor_principal': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'coautores': ModelSelect2MultipleWidget(
                model=User,
                search_fields=['email__icontains'],
                attrs={'class': 'form-control'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_chamada'].widget.attrs['hx-trigger'] = 'load, change'
        self.populate_initial_document_fields()

        self.helper.layout[0].append(Column('documento_n_identificado', css_class='col-md-12 px-0'))
        self.helper.layout[0].append(Column('documento_identificado', css_class='col-md-12 px-0'))
        self.helper.layout[0].append(Column('ciencia', css_class='col-md-12 px-2'))

    def populate_initial_document_fields(self):
        if self.instance.pk:
            self.populate_initial_document('documento_n_identificado', 'primeira_chamada')
            self.populate_initial_document('documento_identificado', 'ultima_chamada')

    def populate_initial_document(self, field, chamada_type):
        chamada = getattr(self.instance.tipo_chamada, chamada_type, None)
        if chamada:
            submissao = self.instance.submissoes.filter(chamada=chamada).first()
            if submissao and submissao.documento:
                self.fields[field].initial = submissao.documento.file

    def clean_documento_identificado(self):
        return self.validate_file_format('documento_identificado', ['doc', 'docx'])

    def clean_documento_n_identificado(self):
        return self.validate_file_format('documento_n_identificado', ['pdf'])

    def validate_file_format(self, field_name, allowed_extensions):
        file = self.cleaned_data.get(field_name)
        if file and file.name.split('.')[-1].lower() not in allowed_extensions:
            raise forms.ValidationError(f"O {field_name.replace('_', ' ')} deve estar no formato {', '.join(allowed_extensions).upper()}.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        tipo_chamada = cleaned_data.get('tipo_chamada')
        
        self.validate_chamada_aberta(tipo_chamada)
        self.validate_documentos_obrigatorios(tipo_chamada)

        return cleaned_data

    def validate_chamada_aberta(self, tipo_chamada):
        chamada_atual = tipo_chamada.chamada_atual if tipo_chamada else None
        if chamada_atual and chamada_atual.etapa == EtapaChamada.INICIAL and chamada_atual.status != StatusChamada.ABERTO:
            self.add_error('tipo_chamada', "Não é possível submeter trabalhos para esta chamada. A chamada inicial não está aberta.")

    def validate_documentos_obrigatorios(self, tipo_chamada):
        if tipo_chamada:
            if hasattr(tipo_chamada,"primeira_chamada") and tipo_chamada.primeira_chamada and tipo_chamada.primeira_chamada.tem_submissao and not self.cleaned_data.get('documento_n_identificado'):
                self.add_error('documento_n_identificado', 'Documento não identificado é obrigatório na etapa inicial desta chamada.')
            
            if hasattr(tipo_chamada,"ultima_chamada") and tipo_chamada.ultima_chamada and tipo_chamada.ultima_chamada.tem_submissao and not self.cleaned_data.get('documento_identificado'):
                self.add_error('documento_identificado', 'Documento identificado é obrigatório na etapa final desta chamada.')
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.save()
        chamadas = instance.tipo_chamada.chamadas.all()  # Obter todas as chamadas associadas ao tipo de chamada
        for chamada in chamadas:
            self.create_or_update_submission(instance, chamada)

        return instance

    def create_or_update_submission(self, instance, chamada):
        submissao, created = instance.submissoes.get_or_create(chamada=chamada)
        documento = None
        if chamada.etapa == EtapaChamada.INICIAL:
            # Se for inicial, adiciona o documento não identificado, se presente
            documento_n_identificado = self.cleaned_data.get('documento_n_identificado')
            if documento_n_identificado:
                documento = Documento.objects.create(
                    file=documento_n_identificado,
                    tipo=TipoDocumento.TRABALHO,
                    descricao=f'Documento da Chamada Inicial - {instance.id}'
                )
                
        elif chamada.etapa == EtapaChamada.FINAL:
            # Se for final, adiciona o documento identificado, se presente
            documento_identificado = self.cleaned_data.get('documento_identificado')
            if documento_identificado:
                documento = Documento.objects.create(
                    file=documento_identificado,
                    tipo=TipoDocumento.TRABALHO,
                    descricao=f'Documento da Chamada Final - {instance.id}'
                )
        else:
            # Para outras chamadas, cria uma submissão sem arquivo, com nome e ID do trabalho
            documento = Documento.objects.create(
                tipo=TipoDocumento.TRABALHO,
                descricao=f'Documento associado à chamada {chamada} sem arquivo.'
            )

        if documento:
            submissao.documento = documento
            submissao.save()

class TrocarDocSubmissaoForm(forms.ModelForm):
    novo_arquivo = forms.FileField(required=True, label="Novo Arquivo")
    ciencia = forms.BooleanField(required=True, label="Declaro que estou ciente de todas as informações contidas nas orientações da chamada e que as informações declaradas por mim neste formulário são de minha inteira responsabilidade.")
    
    class Meta:
        model = Submissao
        fields = ['trabalho','chamada','documento', 'novo_arquivo', 'ciencia']
        widgets = {
            'trabalho': forms.Select(
                attrs={
                    'class': 'form-control',
                    'readonly': 'readonly',
                }
            ),
            'chamada': forms.Select(
                attrs={
                    'class': 'form-control',
                    'readonly': 'readonly',
                }
            ),
            'documento':forms.Select(
                attrs={
                    'class': 'form-control',
                    'readonly': 'readonly',
                }
            )
        }

    
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("chamada", css_class="col-md-3"),
                Column("trabalho", css_class="col-md-9"),
                Column("documento", css_class="col-md-12"),
                Column("novo_arquivo", css_class="col-md-12"),
                Column("ciencia", css_class="col-md-12 mx-2"),
            ),
        )
    )
    
    def save(self, commit=True):
        cleaned_data = super().clean()
        instance = super().save(commit=False)

        novo_arquivo = cleaned_data.get('novo_arquivo')

        if instance.documento is None:
            instance.documento = Documento.objects.create(descricao=f"Documento Trabalho {instance.trabalho.id}", file=novo_arquivo, tipo=TipoDocumento.TRABALHO)

        if novo_arquivo:
            instance.documento.file = novo_arquivo
            instance.documento.save()

        instance.save()
        return instance

class AvaliacaoForm(forms.ModelForm):    

    class Meta:
        model = Avaliacao
        fields = [ 'avaliador', 'dt_limite_aceite']
        widgets = {
             'avaliador': ModelSelect2Widget(
                model=Avaliador,
                required=True,
                search_fields=['usuario__email__icontains'],
                attrs={
                    'class': 'form-control',
                    'data-minimum-input-length': 3 
                }, 
            ),
            'dt_limite_aceite': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.submissao = kwargs.pop('submissao', None)        
        super().__init__(*args, **kwargs)
        if self.submissao:
            self.trabalho = self.submissao.trabalho
            qs = Avaliador.objects.filter(evento=self.trabalho.tipo_chamada.evento, areas_tematicas=self.trabalho.area_tematica)
            qs = qs.exclude(usuario__in=self.submissao.avaliacoes.values_list('avaliador__usuario', flat=True))
            qs = qs.exclude(usuario__in=self.submissao.trabalho.autores).order_by('usuario__first_name')
            self.fields['avaliador'].queryset = qs.all()


    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("avaliador", css_class="col-md-9"),
                Column("dt_limite_aceite", css_class="col-md-3"),
            ),
        )
    )
    
class AvaliacaoTrabalhoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = [ 'status', 'nota_parcial', 'comentario']
        widgets = {
            'status': forms.Select(choices=StatusAvaliacao.choices),
            'nota_parcial': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'comentario': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            chamada_etapa = self.instance.submissao.chamada.etapa
            if chamada_etapa == EtapaChamada.INICIAL:
                self.fields['status'].widget = forms.Select(choices=[
                    (StatusAvaliacao.EM_AVALIACAO, "Em Avaliação"),
                    (StatusAvaliacao.ACEITO, "Aceito"),
                    (StatusAvaliacao.ACEITO_C_RESSALVAS, "Aceito com Ressalvas"),
                    (StatusAvaliacao.RECUSADO, "Recusado"),
                ])
            elif chamada_etapa == EtapaChamada.APRESENTACAO:
                self.fields['status'].widget = forms.Select(choices=[
                    (StatusAvaliacao.EM_AVALIACAO, "Em Avaliação"),
                    (StatusAvaliacao.APRESENTADO, "Apresentado"),
                    (StatusAvaliacao.NAO_APRESENTADO, "Não Apresentado"),
                ])
            else:
                self.fields['status'].widget = forms.Select(choices=[
                    (StatusAvaliacao.EM_AVALIACAO, "Em Avaliação"),
                    (StatusAvaliacao.CONCLUIDA, "Concluída"),
                ])

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("comentario", css_class="col-md-12"),
                Column("status", css_class="col-md-10"),
                Column("nota_parcial", css_class="col-md-2"),
            ),
        )
    )
        

class AvaliacaoCriterioForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoCriterio
        fields = ['criterio', 'nota_criterio', 'comentario']
        widgets = {
            'criterio': forms.Select(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'nota_criterio': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'comentario': forms.Textarea(attrs={'rows': 2}),
        }    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            chamada = self.instance.criterio.chamada
            if chamada.forma_avaliacao == FormaAvaliacao.SOMA:
                self.fields['nota_criterio'].widget =  forms.NumberInput(attrs={'min': 0, 'max': self.instance.criterio.peso})
            else:
                self.fields['nota_criterio'].widget =  forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1})
            
        
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("criterio", css_class="col-md-12"),
                Column("nota_criterio", css_class="col-md-12"),
                Column("comentario", css_class="col-md-12"),
            ),
        )
    )


    
class AvaliacaoCriterioInline(InlineFormSetFactory):
    model = AvaliacaoCriterio
    form_class = AvaliacaoCriterioForm
    factory_kwargs = dict(extra=0, can_delete=False, fk_name="avaliacao")