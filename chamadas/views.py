from typing import Any
from django import forms
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from core.views import CreateWithInlinesView, DeleteView, DetailView, EditWithInlinesView, TableListView

from chamadas.forms import ChamadaCriterioInline, ChamadaForm, TipoChamadaDocumentoInline, TipoChamadaForm
from chamadas.models import FormaAvaliacao, TipoChamada, Chamada
from core.views import DeleteView, DetailView, EditWithInlinesView, TableListView
from core.viewsets import ViewSet
from .filtersets import ChamadaFilter, TipoChamadaFilter

tipo_chamadas_vs = ViewSet(TipoChamada)
chamadas_vs = ViewSet(Chamada)

@tipo_chamadas_vs.action('add')
class TipoChamadaCreateView(CreateWithInlinesView):
    model = TipoChamada
    permission_required = ["is_admin_rule"]
    form_class = TipoChamadaForm
    inlines = [TipoChamadaDocumentoInline]
    inlines_names = ["doc_forms"]
    template_name = "tipo_chamada_form.html"
    def get_success_url(self) -> str:
        return reverse("evento:evento-tipochamadas")
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return TipoChamada(evento=self.request.evento)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        form = self.get_form(self.get_form_class())
        inlines = self.construct_inlines()

        if form.is_valid() and all(inline_formset.is_valid() for inline_formset in inlines):
            return self.forms_valid(form, inlines)
        else:
            return self.forms_invalid(form, inlines)
    
    def forms_valid(self, form, inlines):
        # Salva o formulário principal (chamada)
        chamada = form.save(commit=False)
        chamada.evento = self.request.evento
        chamada.save()

        # Salva os formulários inline (deadline)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    inline_instance = f.save(commit=False)
                    inline_instance.chamada = chamada
                    inline_instance.save()
        return super().forms_valid(form, inlines)

@tipo_chamadas_vs.action('edit')
class TipoChamadaEditView(EditWithInlinesView):
    model = TipoChamada
    permission_required = ["is_admin_rule", "is_member_rule"]
    form_class = TipoChamadaForm
    inlines = [TipoChamadaDocumentoInline]
    inlines_names = ["doc_forms"]
    template_name = "tipo_chamada_form.html"
    def get_success_url(self) -> str:
        return reverse("evento:evento-tipochamadas")
    
    def get_object(self, queryset=None):
        self.object = get_object_or_404(TipoChamada, pk=self.kwargs.get("pk"))
        return self.object
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        form = self.get_form(self.get_form_class())
        inlines = self.construct_inlines()

        # Verifica se o formulário principal e os inlines são válidos
        if form.is_valid() and all(inline_formset.is_valid() for inline_formset in inlines):
            return self.forms_valid(form, inlines)
        else:
            return self.forms_invalid(form, inlines)
        
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def forms_valid(self, form, inlines):
        # Salva o formulário principal (chamada)
        chamada = form.save(commit=False)
        chamada.evento = self.request.evento
        chamada.save()

        # Salva os formulários inline (deadline)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    inline_instance = f.save(commit=False)
                    inline_instance.chamada = chamada
                    inline_instance.save()
                        
        return super().forms_valid(form, inlines)

@tipo_chamadas_vs.action('detail')
class TipoChamadaDetailView(DetailView):
    model = TipoChamada
    detail_fields = ['nome']
    permission_required = ["is_admin_rule", "is_member_rule"]

@tipo_chamadas_vs.action('delete')
class TipoChamadaDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]
    def get_success_url(self) -> str:
        return reverse("evento:evento-tipochamadas")
    


@chamadas_vs.action('list')
class ChamadaListView(TableListView):
    model = Chamada
    filterset_class = ChamadaFilter
    list_display =["tipo__nome", "etapa", "dt_inicio", "dt_encerramento","status"]
    permission_required = ["is_admin_rule", "is_member_rule"]
    def get_queryset(self):
        return super().get_queryset().filter(tipo__evento = self.request.evento)
    
@chamadas_vs.action('add')
class ChamadaCreateView(CreateWithInlinesView):
    model = Chamada
    permission_required = ["is_admin_rule"]
    form_class = ChamadaForm
    inlines = [ChamadaCriterioInline]
    inlines_names = ["criterio_forms"]
    template_name = "chamada_form.html"

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        initial_object = self.object
        if form.is_valid():
            self.object = form.save(commit=False)
            form_validated = True
        else:
            form_validated = False

        if self.object and self.object.forma_avaliacao == FormaAvaliacao.SEM:
            return super().form_valid(form)
        
        inlines = self.construct_inlines()

        if all([formset.is_valid() for formset in inlines]) and form_validated:
            return self.forms_valid(form, inlines)
        self.object = initial_object
        return self.forms_invalid(form, inlines)
    
    def forms_valid(self, form, inlines):
        deadline = form.save(commit=False)
        deadline.save()

        # Salva os formulários inline (criterio)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    ck = f.clean()
                    if len(ck) <= 0:
                        continue
                    inline_instance = f.save(commit=False)
                    inline_instance.deadline = deadline
                    inline_instance.save()
                        
        return super().forms_valid(form, inlines)
@chamadas_vs.action('edit')
class ChamadaEditView(EditWithInlinesView):
    model = Chamada
    permission_required = ["is_admin_rule", "is_member_rule"]
    form_class = ChamadaForm
    inlines = [ChamadaCriterioInline]
    inlines_names = ["criterio_forms"]
    template_name = "chamada_form.html"
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        initial_object = self.object
        form_validated = form.is_valid()
        self.object = initial_object
        
        if form_validated:
            self.object = form.save(commit=False)
        
        inlines = self.construct_inlines()
        
        if self.object.forma_avaliacao == FormaAvaliacao.SEM:
            self.object.criterios_avaliacao.all().delete()
            return super().form_valid(form) if form_validated else super().forms_invalid(form, inlines)
            
       
        if all(formset.is_valid() for formset in inlines) and form_validated:
            return self.forms_valid(form, inlines)

       
        return self.forms_invalid(form, inlines)
    
    def forms_valid(self, form, inlines):
        chamada = form.save(commit=False)
        chamada.save()

        for inline_formset in inlines:
            for f in inline_formset:
                if f.is_valid():
                    ck = f.clean()
                    if not ck:
                        continue
                    inline_instance = f.save(commit=False)
                    inline_instance.deadline = chamada
                    inline_instance.save()
                        
        return super().forms_valid(form, inlines)

    
    
@chamadas_vs.action('detail')
class ChamadaDetailView(DetailView):
    model = Chamada
    detail_fields = ['tipo__nome','etapa', 'dt_inicio', 'dt_encerramento', 'status']
    permission_required = ["is_admin_rule", "is_member_rule"]

@chamadas_vs.action('delete')
class ChamadasDeadlineDeleteView(DeleteView):
    permission_required = ["is_admin_rule", "is_member_rule"]
