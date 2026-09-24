from typing import Any
from django.db.models.base import Model as Model

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from core.views import CreateView, DeleteView, DetailView, FormView,  TableListView
from submissao.forms import AvaliacaoForm, MeuTrabalhoForm

from submissao.models import Avaliacao,  Submissao
from core.viewsets import ViewSet
from .filtersets import SubmissaoFilter
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .tables import SubmissaoTable
from django.db.models import Q

submissoes_vs = ViewSet(Submissao)
avaliacoes_vs = ViewSet(Avaliacao)
@submissoes_vs.action('list')
class SubmissaoListView(TableListView):
    model = Submissao
    
    permission_required = ["is_admin_rule"]
    filterset_class = SubmissaoFilter
    table_class = SubmissaoTable
    template_name = "submissao_list.html"

    def get_queryset(self):
        qs = Submissao.objects.filter(chamada__tipo__evento=self.request.evento).distinct()
        etapa = self.request.GET.get('etapa')
        if etapa:
            qs = qs.filter(chamada__etapa=etapa.lower())
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Submissões Cadastradas")
        etapa = self.request.GET.get('etapa')
        context['etapa'] = etapa.lower() if etapa else None
        return context
    
@submissoes_vs.action('detail')
class DetalharSubmissaoView(DetailView):
    model = Submissao
    template_name = "submissao_detail.html"
    context_object_name = "submissao"
    permission_required = ["is_admin_rule"]

@avaliacoes_vs.action('add',route='<int:submissao_id>/add_avaliacao')
class AvaliacaoCreateView(CreateView):
    form_class = AvaliacaoForm
    permission_required = ["is_admin_rule"]

    def get_object(self, queryset = ...):
        self.submissao = get_object_or_404(Submissao, id=self.kwargs.get('submissao_id'))
        self.object = Avaliacao(submissao=self.submissao)
        return self.object
    
    def get_form_kwargs(self):
        self.object = self.get_object()
        kwargs = super().get_form_kwargs()
        kwargs['submissao'] = self.submissao
        kwargs['instance'] = self.object
        return kwargs

    def get_success_url(self):
        return reverse('submissao:submissao-detail', kwargs={'pk': self.submissao.pk})

@avaliacoes_vs.action('detail', modal=True, route='<int:submissao_id>/detail_avaliacao/<int:pk>')
class AvaliacaoDetailView(DetailView):
    detail_fields = ['avaliador', 'nota_parcial', 'status', 'comentario', 'criterios_detail']
    template_name = "modal_detail.html"
    permission_required = ["is_admin_rule"]
    def get_object(self, queryset = ...):
        self.submissao = get_object_or_404(Submissao, id=self.kwargs.get('submissao_id'))
        self.object = Avaliacao.objects.get(id=self.kwargs.get('pk'))
        return self.object
    
    def get_success_url(self):
        return reverse('submissao:submissao-detail', kwargs={'pk': self.submissao.pk})

@avaliacoes_vs.action('delete', modal=True, route='<int:submissao_id>/delete_avaliacao/<int:pk>')
class AvaliacaoDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]

    def get_object(self, queryset = ...):
        self.submissao = get_object_or_404(Submissao, id=self.kwargs.get('submissao_id'))
        self.object = Avaliacao.objects.get(id=self.kwargs.get('pk'))
        return self.object
    
    def get_success_url(self):
        return reverse('submissao:submissao-detail', kwargs={'pk': self.submissao.pk})
