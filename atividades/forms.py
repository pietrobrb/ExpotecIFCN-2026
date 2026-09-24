from datetime import date
from django import forms
from django.urls import reverse_lazy
from extra_views import InlineFormSetFactory

from usuarios.models import User
from .models import Agendamento, Atividade, PapelResponsavel, Responsavel, Sala, StatusAtividade, TipoAtividade
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, Div
from core.forms import DateInput, ModelSelect2Widget
from django_summernote.widgets import SummernoteWidget    
from django.utils.translation import gettext_lazy as _
class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = [
            'titulo', 
            'descricao', 
            'publico', 
            'pre_requisitos', 
            'objetivos', 
            'conteudo', 
            'materiais', 
            'metodologia', 
            'referencias', 
            'com_inscricoes',
            'qtd_vagas', 
            'inicio_inscricoes', 
            'fim_inscricoes', 
            'duracao', 
            'status', 
            'tipo']
         
        widgets = {
            'descricao': SummernoteWidget(),
            'pre_requisitos': SummernoteWidget(),
            'objetivos': SummernoteWidget(),
            'conteudo': SummernoteWidget(),
            'materiais': SummernoteWidget(),
            'metodologia': SummernoteWidget(),
            'referencias': SummernoteWidget(),
            'inicio_inscricoes': DateInput(),
            'fim_inscricoes': DateInput(),
            "com_inscricoes": forms.CheckboxInput(
                attrs={
                    "hx-trigger": "load, change",
                    "hx-get": reverse_lazy("atividade:atividade-get_atividade_partial"),
                    "hx-target": "#add_on",
                    "class": "form-check-input",
                }
            ),
            'duracao': forms.TextInput(attrs={"type"  :"time"})
        }

    def __init__(self, *args, **kwargs):
        atividade = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if atividade and atividade.pk:
            self.fields['com_inscricoes'].widget.attrs['hx-get'] = reverse_lazy(
                "atividade:atividade-get_atividade_partial", kwargs={"pk": atividade.pk}
            )
        else:
            self.fields['com_inscricoes'].widget.attrs['hx-get'] = reverse_lazy(
                "atividade:atividade-get_atividade_partial", kwargs={"pk": 0}
            )

    def clean(self):
        cleaned_data = super().clean()
        com_inscricoes = cleaned_data.get('com_inscricoes')
        qtd_vagas = cleaned_data.get('qtd_vagas')
        inicio_inscricoes = cleaned_data.get('inicio_inscricoes')
        fim_inscricoes = cleaned_data.get('fim_inscricoes')
        status = cleaned_data.get('status')

        if com_inscricoes:
            if qtd_vagas is None:
                self.add_error('qtd_vagas', "Quantidade de Vagas é obrigatória quando permitido inscrições.")
                raise forms.ValidationError("Quantidade de Vagas é obrigatória quando permitido inscrições.")
            if not inicio_inscricoes:
                self.add_error('inicio_inscricoes', "Data de início das inscrições é obrigatória.")
                raise forms.ValidationError("Data de início das inscrições é obrigatória.")
            if not fim_inscricoes:
                self.add_error('fim_inscricoes', "Data de fim das inscrições é obrigatória.")
                raise forms.ValidationError("Data de fim das inscrições é obrigatória.")

            today = date.today()

            # Calcular status com base nas datas de início e fim das inscrições
            if inicio_inscricoes and fim_inscricoes:
                if inicio_inscricoes >= fim_inscricoes:
                    self.add_error('fim_inscricoes', "A data de fim das inscrições deve ser posterior à data de início.")
                    raise forms.ValidationError("A data de fim das inscrições deve ser posterior à data de início.")


                # Atualiza o status com base nas datas
                if today < inicio_inscricoes:
                    status = StatusAtividade.INSCRICOES_EMBREVE if status != StatusAtividade.RASCUNHO else status
                elif inicio_inscricoes <= today <= fim_inscricoes:
                    status = StatusAtividade.INSCRICOES_ABERTAS if status != StatusAtividade.RASCUNHO else status
                elif today > fim_inscricoes:
                    status = StatusAtividade.INSCRICOES_ENCERRADAS if status != StatusAtividade.RASCUNHO else status
                else:
                    StatusAtividade.RASCUNHO 

            # Define o status no cleaned_data
            cleaned_data['status'] = status
        return cleaned_data
    
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("tipo", css_class="col-md-4"),
                Column("titulo", css_class="col-md-8"),
                Column("duracao", css_class="col-md-4"),
                Column("publico", css_class="col-md-5"),
                Column("com_inscricoes", css_class="col-md-3 form-check pt-4"),
                Div(id="add_on", css_class="col-md-12"),
                Column("descricao", css_class="col-md-12"),
                Column("objetivos", css_class="col-md-12"),
                Column("conteudo", css_class="col-md-12"),
                Column("metodologia", css_class="col-md-12"),
                Column("pre_requisitos", css_class="col-md-12"),
                Column("materiais", css_class="col-md-12"),
                Column("referencias", css_class="col-md-12"),
            ),
        )
    )


class EventoTipoAtividadeForm(forms.ModelForm):
    class Meta:
        model = TipoAtividade
        fields = ['nome', 'descricao', 'cor', 'icone']
        widgets = {
            'cor': forms.TextInput(attrs={'type': 'color'}),
        }

    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("nome", css_class="col-md-4"),
                Column("descricao", css_class="col-md-8"),
                Column("cor", css_class="col-md-2"),
                Column("icone", css_class="col-md-2"),
            ),
        )
    )


class EventoSalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade']
        widgets = {
            'capacidade': forms.NumberInput(attrs={'min': 0, 'max': 1000}),
        }
    
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("nome", css_class="col-md-8"),
                Column("capacidade", css_class="col-md-4"),
            ),
        )
    )

class EventoAgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['atividade', 'sala', 'dia', 'inicio', 'fim']
        widgets = {
            'dia': DateInput(),
            'inicio': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'fim': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'atividade': ModelSelect2Widget(
                model=Atividade,
                required=True,
                search_fields=['titulo__icontains'],
                attrs={
                    'class': 'form-control w-100',
                    'data-minimum-input-length': 0
                },
            ),
            'sala': ModelSelect2Widget(
                model=Sala,
                required=True,
                search_fields=['nome__icontains'],
                attrs={
                    'class': 'form-control w-100',
                    'data-minimum-input-length': 0
                },
            ),
        }
    
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            Row(
                Column("atividade", css_class="col-md-8"),
                Column("sala", css_class="col-md-4"),
                Column("dia", css_class="col-md-4"),
                Column("inicio", css_class="col-md-4"),
                Column("fim", css_class="col-md-4"),
            ),
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get("inicio")
        fim = cleaned_data.get("fim")
        sala = cleaned_data.get("sala")
        dia = cleaned_data.get("dia")
        atividade = cleaned_data.get("atividade")

        
        if fim and inicio and fim <= inicio:
            self.add_error('fim', _("A hora de término deve ser posterior à hora de início."))

        # Verifica se a sala já tem um agendamento no mesmo horário
        if sala and dia and inicio and fim:
            agendamentos_existentes = Agendamento.objects.filter(
                sala=sala,
                dia=dia,
                inicio__lt=fim,  
                fim__gt=inicio   
            )
            if self.instance.pk:
                agendamentos_existentes = agendamentos_existentes.exclude(pk=self.instance.pk)
                
            if agendamentos_existentes.exists():
                self.add_error('sala', _("A sala já está reservada para o horário selecionado."))
        
        evento = atividade.tipo.evento
        if evento:
            if dia < evento.dt_inicio:
                self.add_error('dia', _("O agendamento não pode ser anterior à data de início do evento."))
            if dia > evento.dt_encerramento:
                self.add_error('dia', _("O agendamento não pode ser posterior à data de encerramento do evento."))

        return cleaned_data
                

class ResponsavelAtividadeForm(forms.ModelForm):
    nome_completo = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(
            attrs={'class': 'form-control select_user',
                'onchange': 'getUserData(this);',
            })
        )
    papel = forms.ChoiceField(choices=PapelResponsavel.choices, required=True, widget=forms.Select())
    usuario = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=forms.HiddenInput())

    class Meta:
        model = Responsavel
        fields = ['email', 'nome_completo', 'papel', 'usuario']
        


    def __init__(self, membro=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        if self.instance.pk and self.instance.usuario and self.instance.usuario.pk:
            user = self.instance.usuario
            self.fields['nome_completo'].initial = user.nome_completo
            self.fields['email'].initial = user.email
            self.fields['papel'].initial = self.instance.papel
            readonly_fields = [ 'nome_completo']
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
                Column("email", css_class="col-md-4"),
                Column("nome_completo", css_class="col-md-5"),
                Column("papel", css_class="col-md-3"),    
            )   
        )
    )
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and hasattr(self.instance,"atividade"):
            if self._meta.model.objects.filter(atividade=self.instance.atividade, usuario__email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este usuário já foi incluído como responsável nesta atividade.')
            
        return email


class ResponsavelAtividadeInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        autor_principal_count = 0

        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                continue  # Ignorar se o formulário está marcado para exclusão

            papel = form.cleaned_data.get('papel')
            if papel == PapelResponsavel.AUTOR_PRINCIPAL:
                autor_principal_count += 1

        if autor_principal_count > 1:
            raise forms.ValidationError("Somente um responsável pode ser designado como Autor Principal por atividade.")
        
class ResponsavelAtividadeInline(InlineFormSetFactory):
    model = Responsavel
    form_class = ResponsavelAtividadeForm
    formset_class = ResponsavelAtividadeInlineFormSet  # Use o formset customizado
    factory_kwargs = dict(extra=0, can_delete=True, fk_name="atividade")


