from django.shortcuts import redirect, render
from typing import Any
from django import forms
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from core.views import CreateView, DetailView, TableListView
from core.viewsets import ViewSet
from credenciamento.forms import InscricaoAtividadeFilter, InscricaoAtividadeForm, InscricaoEventoFilter
from eventos.models import InscricaoEvento
from usuarios.models import User
from atividades.models import Atividade, InscricaoAtividade, TipoAtividade
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse



credenciamento_vs = ViewSet(InscricaoEvento)
presenca_vs = ViewSet(InscricaoAtividade)

@credenciamento_vs.action("list")
class InscricaoEventoListView(TableListView):
    model = InscricaoEvento
    template_name = 'inscricoes_evento_list.html'
    context_object_name = 'inscricoes'
    paginate_by = 10
    permission_required = ["is_admin_rule", "is_member_rule"]


    def get_queryset(self):
        queryset = InscricaoEvento.objects.filter(evento=self.request.evento)
        vinculo = self.request.GET.get('vinculo')
        email = self.request.GET.get('email')

        if vinculo:
            queryset = queryset.filter(usuario__vinculo=vinculo)
        if email:
            queryset = queryset.filter(usuario__email__icontains=email)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtro = InscricaoEventoFilter(self.request.GET, queryset=self.get_queryset())
        context['filtro_form'] = filtro.form
        context['page_title'] = "Credenciar Participantes"
        return context

    def post(self, request, *args, **kwargs):
        inscricao_id = request.POST.get('inscricao_id')
        credenciado = request.POST.get('credenciado') == 'true'

        inscricao = get_object_or_404(InscricaoEvento, id=inscricao_id)
        inscricao.credenciado = credenciado
        inscricao.save()

        return JsonResponse({'success': True, 'credenciado': inscricao.credenciado})
    



@presenca_vs.action("list")
class InscricaoAtividadeListView(TableListView):
    model = InscricaoAtividade
    template_name = 'inscricoes_atividade_list.html'
    context_object_name = 'inscricoes'
    paginate_by = 10
    permission_required = ["is_admin_rule", "is_member_rule"]


    def get_queryset(self):
        queryset = InscricaoAtividade.objects.all()
        tipo_atividade_id = self.request.GET.get('tipo')     
        email = self.request.GET.get('email')

        if email:
            queryset = queryset.filter(usuario__email__icontains=email)

        elif tipo_atividade_id:
            tipo_atividade = get_object_or_404(TipoAtividade, id=tipo_atividade_id)
            atividades = Atividade.objects.filter(tipo=tipo_atividade)
            queryset = queryset.filter(atividade__in=atividades)

        filtro = InscricaoAtividadeFilter(self.request.GET, queryset=queryset)
        return filtro.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtro = InscricaoAtividadeFilter(self.request.GET, queryset=self.get_queryset())
        context['filtro_form'] = filtro.form
        context['page_title'] = "Credenciar Atividades"
        return context

    def post(self, request, *args, **kwargs):
        inscricao_id = request.POST.get('inscricao_id')
        presente = request.POST.get('presente') == 'true'

        inscricao = get_object_or_404(InscricaoAtividade, id=inscricao_id)
        inscricao.presente = presente
        inscricao.save()

        return JsonResponse({'success': True, 'presente': inscricao.presente})


@presenca_vs.action('add')
class InscricaoAtividadeCreateView(CreateView):
    template_name = 'inscricao_atividade_form.html'

    def get(self, request, *args, **kwargs):
        form = InscricaoAtividadeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = InscricaoAtividadeForm(request.POST)
        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.usuario = form.cleaned_data['usuario']
            inscricao.save()
            return redirect(reverse_lazy('credenciamento:inscricaoatividade-list'))  
        return render(request, self.template_name, {'form': form})