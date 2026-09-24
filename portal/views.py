from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse

from atividades.filtersets import AgendamentoFilter
from atividades.models import Agendamento
from chamadas.models import TipoChamada
from core.views import PublicDetailView, PublicTableListView
from core.viewsets import ViewSet
from eventos.models import AreaTematica, Evento
from django.views.generic import TemplateView

from portal.tables import PortalAgendamentoTable

portal_vs = ViewSet(Evento)
@portal_vs.action("portal")
class PortalEventoView(PublicDetailView):
    model = Evento
    template_name = "index.html"
    permission_required = []

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.evento
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@portal_vs.action("atividades")
class EventoAgendaListView(TemplateView):
    permission_required = ["is_admin_rule", "is_member_rule"]
    def get(self, request, *args, **kwargs):
        return redirect(reverse('portal:evento-list_dia', kwargs={'dia': 1}))



class AtividadesEventoView(PublicTableListView):
    model = Agendamento
    template_name = 'programacao.html'
    filterset_class = AgendamentoFilter
    table_class = PortalAgendamentoTable

    def get_queryset(self):
        qs = Agendamento.objects.filter(sala__evento=self.request.evento).order_by('inicio')
        dias = self.request.evento.dias_do_evento if self.request.evento else None
        if dias:
            id_dia = self.kwargs.get('dia')
            id_dia = int(id_dia)-1
            dia =dias[id_dia] if id_dia < len(dias) else None
            if dia:
                qs = qs.filter(dia=dia)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Programação'
        # Passa o dia atual para o contexto
        context['dia_atual'] = self.kwargs.get('dia')
         # Instanciar o filtro com os parâmetros da requisição
        filterset = self.filterset_class(self.request.GET, queryset=self.get_queryset())

        # Verificar se o campo 'tipo' foi passado no filtro
        if filterset.is_valid():
            context['tipo_atual'] = filterset.form.cleaned_data.get('tipo')

        return context
    
    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        kwargs["extra_columns"] = []
        return kwargs
    
    def get_table_class(self):
        table_class = super().get_table_class()
        table_class._meta.sequence = ["..."] 
        return table_class

@portal_vs.action("chamadas")
class ChamadasEventoView(PublicDetailView):
    model = Evento
    template_name = "chamadas.html"
    permission_required = []

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.evento
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
@portal_vs.action("downloads")
class DownloadsEventoView(PublicDetailView):
    model = Evento
    template_name = "downloads.html"
    permission_required = []

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.evento
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    


@portal_vs.action("comissoes")
class ComissoesEventoView(PublicDetailView):
    model = Evento
    template_name = "organizacao.html"
    permission_required = []

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.evento
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
@portal_vs.action("chamada", route='chamadas/<int:pk>')
class ChamadaDetailView(PublicDetailView):
    model = Evento
    template_name = "chamada_detail.html"
    permission_required = []

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return TipoChamada.objects.get(pk=self.kwargs.get("pk"))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
    
@portal_vs.action("area", route='areas/<int:pk>')
class ChamadaDetailView(PublicDetailView):
    model = Evento
    template_name = "area_detail.html"
    permission_required = []

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return AreaTematica.objects.get(pk=self.kwargs.get("pk"))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
