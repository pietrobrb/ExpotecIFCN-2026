from typing import Any
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from usuarios.models import User
from .filtersets import AgendamentoFilter, AtividadeFilter
from .forms import AtividadeForm, EventoAgendamentoForm, EventoSalaForm, EventoTipoAtividadeForm, ResponsavelAtividadeInline
from core.views import CreateView, DeleteView, DetailView, EditView, EditWithInlinesView, FormView, TableListView, CreateWithInlinesView
from core.viewsets import ViewSet
from .models import Agendamento, Atividade, Sala, TipoAtividade

atividades_vs = ViewSet(Atividade)
tipo_atividades_vs = ViewSet(TipoAtividade)
salas_vs = ViewSet(Sala)
agendamento_vs = ViewSet(Agendamento)

@atividades_vs.action("list")
class EventoAtividadeListView(TableListView):
    model = Atividade
    filterset_class = AtividadeFilter
    list_display=  ['id', 'titulo', 'tipo','inicio_inscricoes', 'status']
    
    def get_queryset(self):
        return self.model.objects.filter(tipo__evento=self.request.evento)

@atividades_vs.action("add")
class EventoAtividadeCreateView(CreateWithInlinesView):
    form_class = AtividadeForm
    inlines = [ResponsavelAtividadeInline]
    inlines_names = ["responsavel_forms"]
    template_name = "atividade_form.html"
    permission_required = ["is_admin_rule", "is_member_rule"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form = self.get_form()
        inlines = context.get('responsavel_forms', [])
        
        inline_errors = any(inline_formset.errors for inline_formset in inlines)
        if form.errors:
            context['tab'] = 1  
        elif inline_errors or inlines.errors:
            context['tab'] = 2
        else:
            context['tab'] = 1  

        return context
    
    
    def get_object(self, queryset=None):
        self.object = None
        return self.object
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def forms_valid(self, form, inlines):
        # Salva o formulário principal (atividade)
        atividade = form.save(commit=False)
        if not(atividade.com_inscricoes):
            atividade.vagas_limitadas = None
            atividade.qtd_vagas = None
            atividade.inicio_inscricoes = None
            atividade.fim_inscricoes = None
            atividade.status = None
        atividade.save()

        # Validar os formulários inline primeiro
        for inline_formset in inlines:
            if not inline_formset.is_valid():
                return super().forms_invalid(form, inlines)
            
        
        # Salva os formulários inline (responsaveis)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    # Verifica se já existe um usuário com o CPF fornecido
                    email = f.cleaned_data['email']
                    user_data = {
                        'nome_completo': f.cleaned_data['nome_completo'],
                    }
                  
                    user, created = User.objects.update_or_create(
                        email=email,
                        defaults=user_data
                    )
                        
                    inline_instance = f.save(commit=False)
                    inline_instance.usuario = user
                    inline_instance.atividade = atividade
                    inline_instance.save()
                        

        # Finalmente, chama o método padrão do Django para redirecionar ou processar a resposta
        return super().form_valid(form)
    
@atividades_vs.action("edit")
class EventoAtividadeEditView(EditWithInlinesView):
    model = Atividade
    form_class = AtividadeForm
    inlines = [ResponsavelAtividadeInline]
    inlines_names = ["responsavel_forms"]
    template_name = "atividade_form.html"
    permission_required = ["is_admin_rule", "is_member_rule"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form = self.get_form()
        inlines = context.get('responsavel_forms', [])
        
        inline_errors = any(inline_formset.errors for inline_formset in inlines)
        if form.errors:
            context['tab'] = 1  
        elif inline_errors or inlines.errors:
            context['tab'] = 2
        else:
            context['tab'] = 1  

        return context
    
    
    
    def get_object(self, queryset=None):
        self.object = get_object_or_404(Atividade, pk=self.kwargs.get("pk"))
        return self.object
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def forms_valid(self, form, inlines):
        # Validar os formulários inline primeiro
        for inline_formset in inlines:
            if not inline_formset.is_valid():
                return super().forms_invalid(form, inlines)
            
        # Salva o formulário principal (atividade)
        atividade = form.save(commit=False)
        if not(atividade.com_inscricoes):
            atividade.vagas_limitadas = None
            atividade.qtd_vagas = None
            atividade.inicio_inscricoes = None
            atividade.fim_inscricoes = None
            atividade.status = None
        atividade.save()

        # Salva os formulários inline (responsaveis)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    # Verifica se já existe um usuário com o CPF fornecido
                    email = f.cleaned_data['email']
                    user_data = {
                        'nome_completo': f.cleaned_data['nome_completo'],
                    }
                  
                    user, created = User.objects.update_or_create(
                        email=email,
                        defaults=user_data
                    )
                        
                    inline_instance = f.save(commit=False)
                    inline_instance.usuario = user
                    inline_instance.atividade = atividade
                    inline_instance.save()
                        

        # Finalmente, chama o método padrão do Django para redirecionar ou processar a resposta
        return super().form_valid(form)
    
@atividades_vs.action("detail")
class EventoAtividadeDetailView(DetailView):
    model = Atividade
    detail_fields = ['id', 'titulo', 'tipo','inicio_inscricoes', 'status']
    template_name = "atividade_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AtividadeForm(instance=self.get_object())
        form.fields['descricao'].widget = forms.Textarea(attrs={'rows': 3})
        form.fields['pre_requisitos'].widget = forms.Textarea(attrs={'rows': 3})
        form.fields['objetivos'].widget = forms.Textarea(attrs={'rows': 3})
        form.fields['conteudo'].widget = forms.Textarea(attrs={'rows': 3})
        form.fields['materiais'].widget = forms.Textarea(attrs={'rows': 3})
        form.fields['metodologia'].widget = forms.Textarea(attrs={'rows': 3})
        form.fields['referencias'].widget = forms.Textarea(attrs={'rows': 3})
        for field in form.fields.values():
            field.widget.attrs['disabled'] = 'disabled'
        context['form'] = form
        return context

@atividades_vs.action("delete")
class EventoAtividadeDeleteView(DeleteView):
    pass

@tipo_atividades_vs.action('add')
class EventoTipoAtividadeCreateView(CreateView):
    model = TipoAtividade
    form_class = EventoTipoAtividadeForm
    permission_required = ["is_admin_rule"]
    
    def get_success_url(self) -> str:
        return reverse("evento:evento-tipoatividades")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@tipo_atividades_vs.action('edit')
class EventoTipoAtividadeEditView(EditView):
    model = TipoAtividade
    form_class = EventoTipoAtividadeForm
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-tipoatividades")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@tipo_atividades_vs.action('detail')
class EventoTipoAtividadeDetailView(DetailView):
    model = TipoAtividade
    detail_fields = ['nome', 'descricao', 'cor', 'icone']
    permission_required = ["is_admin_rule", "is_member_rule"]

@tipo_atividades_vs.action('delete', modal=True)
class EventoTipoAtividadeDeletelView(DeleteView):
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-tipoatividades")

@salas_vs.action("add")
class EventoSalaCreateView(CreateView):
    model = Sala
    form_class = EventoSalaForm
    permission_required = ["is_admin_rule"]
    def get_success_url(self) -> str:
        return reverse("evento:evento-salas")
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@salas_vs.action("edit")
class EventoSalaEditView(EditView):
    model = Sala
    form_class = EventoSalaForm
    permission_required = ["is_admin_rule", "is_member_rule"]
    def get_success_url(self) -> str:
        return reverse("evento:evento-salas")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)


@salas_vs.action("detail")
class EventoSalaDetailView(DetailView):
    model = Sala
    detail_fields = ['id', 'nome', 'capacidade']
    permission_required = ["is_admin_rule", "is_member_rule"]

@salas_vs.action("delete")
class EventoSalaDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]
    
    def get_success_url(self) -> str:
        return reverse("evento:evento-salas")
    

@agendamento_vs.action("list")
class EventoAgendamentoListView(TemplateView):
    permission_required = ["is_admin_rule", "is_member_rule"]
    def get(self, request, *args, **kwargs):
        return redirect(reverse('atividade:agendamento-list_dia', kwargs={'dia': 1}))

@agendamento_vs.action("list_dia", route="<int:dia>")
class EventoAgendamentoListView(TableListView):
    model = Agendamento
    list_display = ['dia', 'atividade__titulo', 'sala__nome', 'inicio', 'fim']
    template_name = 'agendamento_list.html'
    filterset_class = AgendamentoFilter
    permission_required = ["is_admin_rule", "is_member_rule"]
    def get_queryset(self):
        qs = self.model.objects.filter(sala__evento=self.request.evento)
        dias = self.request.evento.dias_do_evento
        if dias:
            id_dia = self.kwargs.get('dia')
            id_dia = int(id_dia)-1
            dia =dias[id_dia] if id_dia < len(dias) else None
            if dia:
                qs = qs.filter(dia=dia)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Agenda'
        # Passa o dia atual para o contexto
        context['dia_atual'] = self.kwargs.get('dia')
        # Instanciar o filtro com os parâmetros da requisição
        filterset = self.filterset_class(self.request.GET, queryset=self.get_queryset())

        # Verificar se o campo 'tipo' foi passado no filtro
        if filterset.is_valid():
            context['tipo_atual'] = filterset.form.cleaned_data.get('tipo')

        return context

@agendamento_vs.action('add')
class EventoAgendamentoCreateView(CreateView):
    model = Agendamento
    form_class = EventoAgendamentoForm
    permission_required = ["is_admin_rule"]


@agendamento_vs.action('detail')
class EventoAgendamentoDetailView(DetailView):
    detail_fields = ['atividade__tipo', 'atividade__titulo', 'sala', 'dia', 'inicio', 'fim']
    permission_required = ["is_admin_rule", "is_member_rule"]
@agendamento_vs.action('edit')
class EventoAgendamentoEditView(EditView):
    model = Agendamento
    form_class = EventoAgendamentoForm
    permission_required = ["is_admin_rule", "is_member_rule"]


@agendamento_vs.action('delete', modal=True)
class EventoAgendamentoDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]


@atividades_vs.action("get_atividade_partial", item=False, hidden=True, route="<int:pk>/get_partial")
class AtividadePartialForm(FormView):
    form_class = AtividadeForm
    permission_required = ["is_admin_rule", "is_member_rule"]
    template_name = "hx/atividade_partial.html"  # Template a ser renderizado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atividade_id = self.kwargs.get("pk")
        if atividade_id:
            atividade = Atividade.objects.get(id=atividade_id)
            context['form'] = self.form_class(instance=atividade)
        else:
            context['form'] = self.form_class()
        return context

    def get(self, request, *args, **kwargs):
        com_inscricoes = request.GET.get("com_inscricoes", None)
        if com_inscricoes:
            context = self.get_context_data(**kwargs)
            # Renderiza o template se com_inscricoes for verdadeiro
            return self.render_to_response(context)
        
        # Retorna uma resposta nula ou vazia, caso com_inscricoes não seja passado
        return render(request, "hx/empty_template.html")