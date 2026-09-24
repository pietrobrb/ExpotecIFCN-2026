
from django.shortcuts import render, redirect
from django.views.generic import CreateView as DjangoCreateView
from django.views.generic import DeleteView as DjangoDeleteView
from django.views.generic import FormView as DjangoFormView
from django.views.generic import UpdateView as DjangoUpdateView
from django.views.generic import ListView as DjangoListView
from django.views.generic import DetailView as DjangoDetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from core.mixins import  DetailMixin, FilteredSingleTableMixin, FormMixin, SuccessMessageMixin, PermissionRequiredMixin
from django.conf import settings
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django_select2.views import AutoResponseView
from extra_views.advanced import (
    BaseCreateWithInlinesView,
    BaseUpdateWithInlinesView,
    NamedFormsetsMixin,
)
class CreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormMixin,
    DjangoCreateView,
):
    success_message = '{name} "{obj}" foi adicionado com êxito.'
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Adicionar {self.model._meta.verbose_name}"
        return context
    


class EditView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormMixin,
    DjangoUpdateView,
):
    success_message = '{name} "{obj}" foi atualizado com êxito.'
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Alterar {self.model._meta.verbose_name}"
        return context
    


class DeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    DjangoDeleteView,
):
    delete_message = (
        "Deseja realmente exluir o {object._meta.verbose_name} <b>{object}</b>?"
    )
    success_message = '{name} "{obj}" foi deletado com êxito.'
    template_name = "confirm_delete.html"
    
    def get_delete_message(self, **kwargs):
        obj = getattr(self, "object", None)
        return self.delete_message.format(object=obj, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Apagar {self.object._meta.verbose_name}"
        context["delete_message"] = self.get_delete_message()
        return context


class FormView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormMixin,
    DjangoFormView,
):
    template_name_suffix = "_form"

class TableListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FilteredSingleTableMixin,
    DjangoListView,
):
    template_name_suffix = "_list"
    template_name = "list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.model._meta.verbose_name_plural.capitalize()
        context["table_page"] = int(self.request.GET.get("page", 1))
        if self.filterset:
            context["object_list"] = self.filterset.qs
        return context


class PublicTableListView(
    FilteredSingleTableMixin,
    DjangoListView,
):
    template_name_suffix = "_list"
    template_name = "list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.model._meta.verbose_name_plural.capitalize()
        if self.filterset:
            context["object_list"] = self.filterset.qs
        return context

class DetailView(
    DetailMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DjangoDetailView,
):
    template_name_suffix = "_detail"
    template_name = "detail.html"
    edit_url = None
    
    def get(self, request, *args, **kwargs):
        self.detail_object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{self.model._meta.verbose_name}"
        return context

class PublicDetailView(
    DetailMixin,
    DjangoDetailView,
):
    template_name_suffix = "_detail"
    template_name = "detail.html"
    edit_url = None
    
    def get(self, request, *args, **kwargs):
        self.detail_object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{self.model._meta.verbose_name}"
        return context

class CustomSelect2ResponseView(AutoResponseView):
    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get("term", request.GET.get("term", ""))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                "results": [
                    {"text": obj["_text"], "id": obj["_id"]}
                    for obj in context["object_list"]
                ],
                "more": context["page_obj"].has_next(),
            },
            encoder=import_string(settings.SELECT2_JSON_ENCODER),
        )
    
class CreateWithInlinesView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormMixin,
    NamedFormsetsMixin,
    BaseCreateWithInlinesView,
):
    template_name_suffix = "_form"
    template_name = "form.html"
    success_message = '{name} "{obj}" foi adicionado com êxito.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Adicionar {self.model._meta.verbose_name}"
        return context

class EditWithInlinesView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormMixin,
    NamedFormsetsMixin,
    BaseUpdateWithInlinesView,
):
    template_name_suffix = "_form"
    template_name = "form.html"
    success_message = '{name} "{obj}" foi atualizado com êxito.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Alterar {self.model._meta.verbose_name}"
        return context
    


class EmBreveView(TemplateView):
    template_name = 'embreve.html'