from typing import Any
from django import forms
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import rules
from atividades.filtersets import AtividadeFilter, AtividadeInscricaoFilter
from atividades.models import Atividade, InscricaoAtividade, StatusAtividade
from chamadas.models import CriterioAvaliacao, StatusChamada, TipoChamada
from core.models import get_hoje
from core.viewsets import ViewSet
from enderecos.models import Endereco
from eventos.forms import EventoNoticiaForm
from submissao.forms import AvaliacaoCriterioInline, AvaliacaoTrabalhoForm, MeuTrabalhoAutoSubmissaoForm, MeuTrabalhoForm, TrocarDocSubmissaoForm
from submissao.models import Avaliacao, AvaliacaoCriterio, StatusAvaliacao, StatusTrabalho, Submissao, Trabalho
from usuarios.forms import InscricaoEventoMuiltForm, MeuPerfilMuiltForm, EventoAvaliadorForm
from usuarios.mixins import MeustrabalhosMixin, MinhasAvaliacoesMixin, MinhasSubmissoesMixin
from usuarios.tables import AtividadeInscricaoTable, MinhasInscricoesAtividadeTable, MeusTrabalhosTable, MinhasAvaliacoesTable
from usuarios.filtersets import InscricaoAtividadeFilter
from usuarios.models import User
from eventos.models import Evento, InscricaoEvento, Avaliador, Monitor, Noticia
from core.views import CreateView, DeleteView, DetailView, EditWithInlinesView, FormView, TableListView, EditView
from eventos.forms import MonitorForm
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

trabalhos_vs = ViewSet(Trabalho)
avaliacoes_vs = ViewSet(Avaliacao)
dashboard_vs = ViewSet(Evento)
atividades_vs = ViewSet(Atividade)
insc_atividades_vs = ViewSet(InscricaoAtividade)
class DashboardView(DetailView):
    model = Evento
    template_name = 'dashboard.html'
    permission_required = ["is_participant_rule"]

    def get_object(self, queryset=None):
        self.usuario = self.request.user
        self.trabalhos_usuario = Trabalho.objects.filter(tipo_chamada__evento=self.request.evento).filter(
            Q(autor_principal=self.request.user) | Q(coautores=self.request.user)
        ).distinct().order_by('tipo_chamada', 'titulo')

        return self.request.evento

    def get_context_data(self, **kwargs):
        self.get_object()
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Dashboard"
        context["trabalhos_usuario"] = self.trabalhos_usuario
        return context

class IndexView(DetailView):
    model = User
    permission_required = ["is_user_rule"]
    
    
    def get_object(self, queryset=None):
        return self.request.evento

    def get(self, request, *args, **kwargs):
        if not(request.evento.inscricoes.filter(usuario = request.user).exists()):
            return redirect('user:minhas_inscricoes')
        else:
            return redirect('user:dashboard')

class InscreverseView(CreateView):
    model = InscricaoEvento
    permission_required = ["is_user_rule"]  
    form_class = InscricaoEventoMuiltForm
    template_name ="inscricao_evento.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        if request.evento.inscricoes.filter(usuario = request.user).exists():
            return redirect('user:minhas_inscricoes')
        return super().get(request, *args, **kwargs)
    
    def get_success_url(self) -> str:
        return reverse('user:minhas_inscricoes')
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()    
        kwargs["instance"] = InscricaoEvento(usuario=self.request.user, evento=self.request.evento)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Realizar Inscrição no evento {self.request.evento} "
        return context

    def form_valid(self, form):
        inscricao = form["inscricao"].save(commit=False)
         # Salva o formulário de endereço, caso haja
        endereco = form['endereco'].save(commit=False)
        endereco.save()

        usuario = form['usuario'].save(commit=False)
        usuario.endereco = endereco
        usuario.save()

        # Associa o endereço ao evento e salva o evento
        inscricao.evento = self.request.evento
        inscricao.usuario = usuario
        inscricao.save()

        return super().form_valid(form)
    


class MeuPerfilEditView(EditView):
    model = User
    permission_required = ["is_user_rule"]  
    form_class = MeuPerfilMuiltForm
    template_name ="meu_perfil.html"

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.user

    def get_success_url(self) -> str:
        return reverse('user:index')
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()    
        usuario = self.get_object()
        kwargs.update(
            instance={
                "usuario": usuario,
                "endereco":  usuario.endereco if usuario.endereco else Endereco(),
            }
        )
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Meu Perfil"
        return context

    def form_valid(self, form):
        endereco = form['endereco'].save(commit=False)
        endereco.save()
        usuario = form['usuario'].save(commit=False)
        usuario.endereco = endereco
        usuario.save()
        return super().form_valid(form)



class  MeuCadastroAvaliadorEditView(EditView):
    model = Avaliador
    form_class = EventoAvaliadorForm
    template_name = 'edit_avaliador.html'
    permission_required = ["is_evaluator_rule"]

    def get_success_url(self) -> str:
        return reverse('user:edit_avaliador')

    def get_object(self):
        self.object, _ = Avaliador.objects.get_or_create(usuario=self.request.user, evento=self.request.evento)        
        return self.object

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.evento = self.request.evento
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Meu Perfil"
        return context
    
class  MeuCadastroAvaliadorAddView(CreateView):
    model = Avaliador
    form_class = EventoAvaliadorForm
    template_name = 'cad_avaliador.html'
    permission_required = ["can_evaluate_rule"]

    def get_success_url(self) -> str:
        return reverse('user:edit_avaliador')

    def get_object(self):
        self.object, _ = Avaliador.objects.get_or_create(usuario=self.request.user, evento=self.request.evento)        
        return self.object

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.evento = self.request.evento
        return super().form_valid(form)



@dashboard_vs.action('ler_noticia',  
                    item=False, 
                    hidden=True, 
                    modal=True, 
                    verbose_name=_("Ler Notícia"),
                    route="ler_noticia/<int:pk>/")
class NotificaLerMaisView(DetailView):
    model = Noticia
    permission_required = ["is_participant_rule"]
    template_name = 'modal_detail.html'
    detail_fields = ['subtitulo', 'texto']

    def get_object(self, queryset=None):
        self.object = Noticia.objects.get(pk=self.kwargs.get('pk'))
        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_object().titulo
        return context

@dashboard_vs.action('ver_atividade',  
                    item=False, 
                    hidden=True, 
                    modal=True, 
                    verbose_name=_("Ver Atividade"),
                    route="ver_atividade/<int:pk>/")
class AtividadeView(DetailView):
    model = Atividade
    permission_required = ["is_participant_rule"]
    template_name = 'modal_detail.html'
    detail_fields = ['titulo', 'tipo', 'descricao', 'publico', 'pre_requisitos']

    def get_object(self, queryset=None):
        self.object = Atividade.objects.get(pk=self.kwargs.get('pk'))
        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        if self.object:
            local = self.object.local.nome if self.object.local else "Em breve"
            dt_inicio = "Em breve"
            if self.object.data_inicio:
                dt_inicio = self.object.data_inicio.strftime('%d/%m')

            context['page_title'] = f'Local: {local} | Início: {dt_inicio}'
        else:
            context['page_title'] = "Atividade"
        return context
   
@trabalhos_vs.action('meus_trabalhos',default=True)
class MeusTrabalhosView(TableListView):
    model = Trabalho
    permission_required =  ["is_participant_rule"] 
    table_class= MeusTrabalhosTable
    
    def get_queryset(self):
        user = self.request.user
        evento = self.request.evento
        qs = Trabalho.objects.filter(tipo_chamada__evento=evento).filter(
            Q(autor_principal=user) | Q(coautores=user)
        ).distinct().order_by('tipo_chamada', 'titulo')
        
        return qs.order_by('tipo_chamada', 'titulo')


    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Meus Trabalhos"
        return context
    
@trabalhos_vs.action('criar', route="criar/")
class MeuTrabalhoCreateView(CreateView):
    model = Trabalho
    form_class = MeuTrabalhoAutoSubmissaoForm
    permission_required = ["is_participant_rule"]
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = Trabalho(autor_principal=self.request.user, status=StatusTrabalho.RASCUNHO)
        kwargs['evento'] = self.request.evento
        kwargs['usuario'] = self.request.user
        return kwargs
    

    def get_success_url(self):
        if self.object:
            return reverse('user:trabalho-detail', kwargs={'pk': self.object.pk})
        return reverse('user:trabalho-meus_trabalhos')
    

@trabalhos_vs.action('edit')
class MeuTrabalhoEditView(MeustrabalhosMixin, EditView):  
    model = Trabalho
    form_class = MeuTrabalhoForm
    template_name = "meu_trabalho_form.html"
    permission_required = ["is_participant_rule"]
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        kwargs['evento'] = self.request.evento
        kwargs['usuario'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user not in self.object.autores:
            messages.error(self.request, "Você não tem permissão para editar este trabalho.")
            return redirect(reverse('user:trabalho-meus_trabalhos'))
        
        if self.object.status != StatusTrabalho.RASCUNHO or self.object.tipo_chamada.primeira_chamada.status != StatusChamada.ABERTO:
            return redirect(reverse('user:trabalho-detail', kwargs={'pk': self.object.pk}))
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        trabalho = self.get_object()

        if trabalho.tipo_chamada.primeira_chamada.status == StatusChamada.ENCERRADO:
            messages.error(self.request, "Não é possível editar o trabalho pois a chamada inicial da etapa foi encerrada.")
            return redirect('user:trabalho-meus_trabalhos')
        
        context['submissoes'] = trabalho.submissoes_p_etapa
        context['page_title'] = f"Trabalho"
        return  context
    
    def get_success_url(self):
        return reverse('user:trabalho-detail', kwargs={'pk': self.object.pk})

@trabalhos_vs.action('detail')
class MeuTrabalhoDetailView(MeustrabalhosMixin, DetailView):
    model = Trabalho
    permission_required = ["is_participant_rule"]
    template_name = "meu_trabalho_detail.html"
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user not in self.object.autores:
            messages.error(self.request, "Você não tem permissão para visualizar este trabalho.")
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trabalho = self.get_object()
        
        form = MeuTrabalhoForm(instance=trabalho)
        for field_name, field in form.fields.items():
            field.widget.attrs['disabled'] = 'disabled'

        context['form'] = form
        context['submissoes'] = trabalho.submissoes_p_etapa
        context['page_title'] = f"Meu Trabalho"

        return context


@trabalhos_vs.action('deletar')
class MeuTrabalhoDeleteView(MeustrabalhosMixin, DeleteView):
    model = Trabalho
    permission_required = ["is_participant_rule"]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user not in self.object.autores:
            messages.error(self.request, "Você não tem permissão para editar este trabalho.")
            return redirect(self.get_success_url())
        
        if self.object.tipo_chamada.primeira_chamada and self.object.tipo_chamada.primeira_chamada.status == StatusChamada.ENCERRADO and self.object.status != StatusTrabalho.RASCUNHO:
            messages.error(self.request, "Não é possível excluir o trabalho pois a chamada inicial da etapa foi encerrada.")
            return redirect(self.get_success_url())

        if self.object.status != StatusTrabalho.RASCUNHO:
            messages.error(request, "Você não pode excluir trabalhos que já foram submetidos.")
            return redirect(self.get_success_url())
        
        return super().get(request, *args, **kwargs)
    


@trabalhos_vs.action('submeter', 
                    icon='fa fa-upload', 
                    item=False, 
                    hidden=True,
                    route="<int:pk>/submeter/",
                    verbose_name=_("submeter"),
                    modal=True)
class MeuTrabalhoSubmitView(MeustrabalhosMixin, EditView):
    model = Trabalho
    permission_required = ["is_participant_rule"]
    confirm_message = 'Depois de submeter o trabalho "<b>{object}</b>, ele não poderá mais ser editado. Tem certeza que deseja submtê-lo"?'
    template_name = "confirm_form.html"
    fields = []

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user not in self.object.autores:
            messages.error(self.request, "Você não tem permissão para editar este trabalho.")
            return redirect(self.get_success_url())
        if self.object.tipo_chamada.primeira_chamada.status == StatusChamada.ENCERRADO:
            messages.error(self.request, "Não é possível submeter o trabalho pois a chamada inicial da etapa foi encerrada.")
            return redirect(reverse('user:trabalho-detail', kwargs={'pk': self.object.pk}))  
        return super().get(request, *args, **kwargs)
    
    def get_confirm_message(self, **kwargs):
        obj = self.get_object()
        return self.confirm_message.format(object=obj)
    
    def form_valid(self, form):
        form.instance.status = StatusTrabalho.SUBMETIDO
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["confirm_message"] = self.get_confirm_message()
        context["page_title"] = f"Submeter Trabalho"
        return context

@trabalhos_vs.action('cancelar_submissao', 
                    icon='fa fa-cancel', 
                    item=False, 
                    hidden=True,
                    route="<int:pk>/cancelar/",
                    verbose_name=_("Cancelar Submissão"),
                    modal=True)
class MeuTrabalhoCancelarSubmitView(MeustrabalhosMixin, DetailView):
    model = Trabalho
    permission_required = ["is_participant_rule"]
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.tipo_chamada.primeira_chamada.status == StatusChamada.ENCERRADO:
            messages.error(self.request, "Não é possível cancelar a submissao  do trabalho pois a chamada inicial da etapa foi encerrada.")
            return redirect(self.get_success_url())
         
        if self.request.user not in self.object.autores:
            messages.error(self.request, "Você não tem permissão para editar este trabalho.")
            return redirect(self.get_success_url())
        
        self.object.status = StatusTrabalho.RASCUNHO
        self.object.save()
        return redirect(self.get_success_url())
    
@trabalhos_vs.action('delete_doc', 
                    item=False, 
                    hidden=True,
                    route="delete_doc/<int:pk>/",
                    verbose_name=_("Remover Documento"),
                    modal=True)
class MeuTrabalhoDeleteDocView(MinhasSubmissoesMixin, DeleteView):
    model = Submissao
    permission_required = ["is_participant_rule"]
    delete_message = (
        "Deseja realmente exluir <b>{object}</b>?"
    )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user not in self.object.trabalho.autores:
            messages.error(self.request, "Você não tem permissão para editar este trabalho.")
            return redirect(self.get_success_url())
        if self.trabalho.autor_principal != self.request.user and self.request.user not in self.trabalho.coautores.all():
            messages.error(request, "Você não pode excluir trabalhos que já foram submetidos.")
            return redirect(self.get_success_url())
        
        if self.object.chamada.tem_submissao:
            messages.error(request, "Não é possível remover a submissão de uma chamada que possui submissão obrigatória.")
            return redirect(self.get_success_url())
    
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, request, *args, **kwargs):
        self.object = self.get_object()               
        self.object.documento.file = None
        self.object.documento.save()
        return redirect(self.get_success_url())
    
@trabalhos_vs.action('trocar_doc',  
                        item=False, 
                        hidden=True, 
                        modal=True, 
                        verbose_name=_("Trocar Documento"),
                        route="trocar_doc/<int:pk>/")
class MeuTrabalhoTrocarDocView(MinhasSubmissoesMixin, EditView):
    model = Submissao
    form_class = TrocarDocSubmissaoForm
    permission_required = ["is_participant_rule"]
    template_name = 'modal_form.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user not in self.object.trabalho.autores:
            messages.error(self.request, "Você não tem permissão para editar este trabalho.")
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Trocar Documento"
        form = TrocarDocSubmissaoForm(instance=self.object)
        context['form'] = form
        return context

@trabalhos_vs.action('get_campos_opcionais', item=False, hidden=True)
class TrabalhoFormPartialForm(FormView):
    form_class = MeuTrabalhoAutoSubmissaoForm

    def get(self, request, *args, **kwargs):
        
        context = super().get_context_data(**kwargs)
        tp_id = request.GET.get('tipo_chamada')
        
        
        if tp_id:
            tipo_chamada = TipoChamada.objects.get(pk=tp_id)
            opcoes = list(tipo_chamada.opcoes)
            context['form'] = MeuTrabalhoAutoSubmissaoForm(instance=Trabalho(tipo_chamada=tipo_chamada))
            context['opcoes'] = opcoes
            return render(request, "hx/opcoes_trabalho.html", context)
        else:
            return HttpResponse()
@avaliacoes_vs.action("minhas_avaliacoes", default=True)
class MinhasAvaliacoesListView(TableListView):
    model = Avaliacao
    permission_required = ["is_evaluator_rule"]
    table_class = MinhasAvaliacoesTable
    
    def get_queryset(self):
        self.avaliador = Avaliador.objects.filter(usuario = self.request.user, evento = self.request.evento).first()
        return super().get_queryset().filter(avaliador = self.avaliador).order_by("submissao__trabalho__titulo")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Minhas Avaliações"
        return context
    

@avaliacoes_vs.action("aceitar_avaliacao", item=True, icon="fa fa-check", verbose_name=_("Avaliar") )
class MinhasAvaliacoesAceitarView(MinhasAvaliacoesMixin, DetailView):
    model = Avaliacao
    permission_required = ["is_evaluator_rule"]
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.avaliador.usuario != self.request.user:
            messages.error(self.request, "Você não tem permissão para aceitar esta avaliação.")
            return redirect(self.get_success_url())
        
        if self.object.submissao.chamada.status != StatusChamada.ENCERRADO:    
            messages.error(self.request, "Não é possível aceitar avaliacao de trabalho com chamada ainda não encerrada.")
            return redirect(self.get_success_url())
        
        if self.object.dt_limite_aceite < get_hoje():    
            messages.error(self.request, "Não é possível aceitar. Prazo para aceitação ultrapassado.")
            self.object.status = StatusAvaliacao.AVALIACAO_CANCELADA
            self.object.save()
            return redirect(self.get_success_url())
        
        self.object.status = StatusAvaliacao.EM_AVALIACAO
        self.object.save()

        criterios = CriterioAvaliacao.objects.filter(chamada = self.object.submissao.chamada)
        for ca in criterios:    
            ac = AvaliacaoCriterio.objects.get_or_create(avaliacao=self.object, criterio=ca, defaults={'nota_criterio': 0})       
            
        return redirect(self.get_success_url())
    
    
@avaliacoes_vs.action("cancelar_avaliacao", item=True, icon="fa fa-xmark", verbose_name=_("Cancelar Avaliação"))
class MinhasAvaliacoesCancelarView(MinhasAvaliacoesMixin, DetailView):
    model = Avaliacao
    permission_required = ["is_evaluator_rule"]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.avaliador.usuario != self.request.user:
            messages.error(self.request, "Você não tem permissão para cancelar esta avaliação.")
            return redirect(self.get_success_url())
        
        if self.object.submissao.chamada.status != StatusChamada.ENCERRADO:    
            messages.error(self.request, "Não é possível cancelar avaliacao de trabalho com chamada ainda não encerrada.")
            return redirect(self.get_success_url())
        
        if  self.object.status != StatusAvaliacao.EM_AVALIACAO:
            messages.error(self.request, "Não é possível cancelar avaliacao já encerrada.")
            return redirect(self.get_success_url())
        
        self.object.status = StatusAvaliacao.AVALIACAO_CANCELADA
        self.object.save()
        return redirect(self.get_success_url())
        

@avaliacoes_vs.action("edit")
class MinhasAvaliacoesEditView(MinhasAvaliacoesMixin, EditWithInlinesView):
    model = Avaliacao
    form_class = AvaliacaoTrabalhoForm
    inlines = [AvaliacaoCriterioInline]
    inlines_names = ["criterio_forms"]
    template_name = "minha_avaliacao_form.html"
    permission_required = ["is_evaluator_rule"]
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.avaliador.usuario != self.request.user:
            messages.error(self.request, "Você não tem permissão para editar esta avaliação.")
            return redirect(self.get_success_url())
        
        if self.object.submissao.chamada.status != StatusChamada.ENCERRADO:    
            messages.error(self.request, "Não é possível avaliar trabalho com chamada ainda não encerrada.")
            return redirect(self.get_success_url())
        
        if self.object.status != StatusAvaliacao.EM_AVALIACAO:
            messages.error(self.request, "Não é possível editar avaliacao que não esteja aceita.")
            return redirect(self.get_success_url())
        
        return super().get(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs    
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = "Minha Avaliação"
        context['submissao'] = self.object.submissao
        return context

@avaliacoes_vs.action('detail')
class MinhaAvaliacaoDetailView(MinhasAvaliacoesMixin, DetailView):
    detail_fields = ['submissao__trabalho__titulo','nota_parcial', 'status','comentario',  'criterios_detail']
    permission_required = ["is_evaluator_rule"]
    template_name = "minha_avaliacao_detail.html"

@atividades_vs.action('list', default=True)
class AtividadesInscricaoListView(TableListView):
    model = Atividade
    permission_required = ["is_participant_rule"]
    filterset_class = AtividadeInscricaoFilter
    table_class = AtividadeInscricaoTable
    def get_queryset(self):
        return super().get_queryset().filter(tipo__evento=self.request.evento, com_inscricoes = True).exclude(inscricoes__usuario = self.request.user).order_by('tipo', 'titulo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Atividades com Inscrição"
        return context

@atividades_vs.action('detail', modal=True, item=False, hidden=True, route="atividade_inscricao/<int:pk>/")
class AtividadesInscricaoDetail(DetailView):
    model = Atividade
    template_name = 'modal_detail.html'
    detail_fields = ['tipo', 'titulo', 'descricao', 'duracao', 'publico', 'pre_requisitos', 'objetivos', 'inicio_inscricoes', 'fim_inscricoes', 'status']
    
    def get_success_url(self):
        return reverse('user:atividade-list')

@atividades_vs.action('inscreverse', modal=True, item=False, hidden=True, route="atividade_inscreverse/<int:pk>/")
class AtividadesInscreverse(EditView):
    fields = []
    model = Atividade
    permission_required = ["is_participant_rule"]
    confirm_message = 'Deseja realmente inscrever-se na atividade: "<b>{object}</b> ?'
    template_name = "confirm_form.html"

    def get_object(self, queryset=None):
        self.object = Atividade.objects.filter(tipo__evento=self.request.evento).get(pk=self.kwargs.get("pk"))
        return self.object
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not(self.object.com_inscricoes):
            messages.error(request, "Esta atividade não permite inscricao.")
            return redirect(self.get_success_url())
    
        if self.object.status != StatusAtividade.INSCRICOES_ABERTAS:
            messages.error(request, "Esta atividade não está com inscrições abertas")
            return redirect(self.get_success_url())
        
        if self.object.inscricoes.filter(usuario = request.user).exists():
            messages.error(request, "Você já está inscrito nesta atividade.")
            return redirect(self.get_success_url())

        return super().get(request, *args, **kwargs)
    
    def get_confirm_message(self, **kwargs):
        obj = self.get_object()
        return self.confirm_message.format(object=obj)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["confirm_message"] = self.get_confirm_message()
        context["page_title"] = f"Realizar inscrição em: {self.object.titulo}"
        return context
   
    
    def form_valid(self, request, *args, **kwargs):
        self.object = self.get_object()               
        inscricao, created = InscricaoAtividade.objects.get_or_create(atividade=self.object, usuario=self.request.user)
        if created:
            messages.success(self.request, "Inscrição realizada com sucesso.")
        return redirect(reverse('user:minhas_inscricoes'))


@insc_atividades_vs.action('list', default=True)
class MinhasInscricoesView(TableListView):
    model = User
    permission_required = ["is_user_rule"]
    template_name = 'minhas_inscricoes.html'    
    table_class = MinhasInscricoesAtividadeTable
    filterset_class = InscricaoAtividadeFilter

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        if not(request.evento.inscricoes.filter(usuario = request.user).exists()):
            return redirect('user:inscreverse')
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return self.request.user.inscricoes_atividades.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Minhas Inscrições"
        return context

@insc_atividades_vs.action('delete')
class MinhasInscricoesDeleteView(DeleteView):
    model = InscricaoAtividade
    permission_required = ["is_participant_rule"]

class  MeuCadastroMonitorAddView(CreateView):
    model = Monitor
    form_class = MonitorForm
    permission_required = ["can_monitor_rule"]

    def get_success_url(self) -> str:
        return reverse('user:edit_monitor')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs
    
    def get_object(self):
        self.object, _ = Monitor.objects.get_or_create(usuario=self.request.user, evento=self.request.evento)        
        return self.object

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.evento = self.request.evento
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Tornar-se Monitor"
        return context


class  MeuCadastroMonitorEditView(EditView):
    model = Monitor
    form_class = MonitorForm
    permission_required = ["is_monitor_rule"]
    template_name = 'edit_monitor.html'
    
    def get_success_url(self) -> str:
        return reverse('user:edit_monitor')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs
    
    def get_object(self):
        self.object, _ = Monitor.objects.get_or_create(usuario=self.request.user, evento=self.request.evento)        
        return self.object

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.evento = self.request.evento
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Cadastro de Monitor"
        return context
