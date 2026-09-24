from django.contrib import messages
from crispy_forms.helper import FormHelper
from django_filters.views import FilterMixin as BaseFilterMixin
from django_tables2 import SingleTableMixin, columns, tables
from django.views.generic.detail import SingleObjectMixin
from django_tables2.utils import Accessor
from collections import OrderedDict
from django.utils.functional import cached_property
from django.contrib.auth.mixins import (
    PermissionRequiredMixin as DjangoPermissionRequiredMixin,
)
from extra_views import InlineFormSetFactory
import rules
from django.utils.text import capfirst
class SuccessMessageMixin:
    success_message = ""

    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message(
            form.cleaned_data, getattr(form, "instance", None)
        )
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data, instance):
        if self.success_message:
            return self.success_message.format(
                name=self.model._meta.verbose_name.title(),
                data=cleaned_data,
                obj=instance,
            )
        
class FormMixin(SuccessMessageMixin):
    def get_form_helper(self):
        helper = FormHelper()
        helper.form_id = getattr(self, "form_id", None)
        return helper

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not hasattr(form, "helper"):
            form.helper = self.get_form_helper()
        if hasattr(form, "layout"):
            if callable(form.layout):
                form.helper.layout = form.layout()
            else:
                form.helper.layout = form.layout
        return form

class FilterMixin(BaseFilterMixin):
    @cached_property
    def filterset(self):
        filterset_class = self.get_filterset_class()
        if filterset_class:
            fs = self.get_filterset(filterset_class)
            # se não houver filtros configurado não é necessário retornar a instancia
            if len(fs.filters) > 0:
                return fs
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context




def table_factory(model, fields=None, view_name=None, extra_attrs=None):
    attrs = {"Meta": type("Meta", (object,), {"model": model, "fields": fields})}
    if view_name is not None:
        link_field = fields[0] if fields else "id"
        column = columns.library.column_for_field(model._meta.get_field(link_field))
        attrs.update(
            {
                link_field: type(column)(
                    attrs=dict(a={"class": "text-gray-800 text-hover-primary mb-1"}),
                    linkify=(view_name, {"pk": tables.Accessor("pk")}),
                )
            }
        )

    if extra_attrs is not None:
        attrs.update(extra_attrs)
    return type("%sTable" % model._meta.object_name, (tables.Table,), attrs)


class FilteredSingleTableMixin(FilterMixin, SingleTableMixin):
    list_display = None
    filterset_fields = []

    def get_table_class(self):
        if not self.table_class:
            return table_factory(
                self.model, self.list_display, view_name=self.list_item_url
            )
        return super().get_table_class()

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        table.order_by = self.get_table_order_by(table)
        return table

    def get_table_pagination(self, table):
        pagination = super().get_table_pagination(table)
        updates = {"page": self.request.GET.get("page")}
        if not isinstance(pagination, dict):
            pagination = {}
        pagination.update(updates)
        return pagination

    def get_table_data(self):
        if self.filterset:
            return self.filterset.qs
        return self.get_queryset()

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page", None)
        if per_page is not None:
            self.request.session["per_page"] = per_page
        return self.request.session.get("per_page", self.paginate_by)

    def get_table_order_by(self, table):
        order_key = f"user-settings/{self.request.path}/order"
        req_order_by = self.request.GET.getlist(table.prefixed_order_by_field)
        if not req_order_by:
            req_order_by = []
        saved_order_by = self.request.session.get(order_key, [])
        new_order_by = req_order_by + [
            f
            for f in saved_order_by
            if f not in req_order_by and f"-{f}" not in req_order_by
        ]
        self.request.session[order_key] = new_order_by
        return new_order_by
    
"""
class SearchMixin:
    search_fields = []

    def filter_queryset(self, queryset):
        orm_lookups = [
            f"{str(search_field)}__icontains" for search_field in self.search_fields
        ]
        or_query = models.Q()
        search_term = self.request.GET.get("search", "")
        for bit in smart_split(search_term):
            if bit.startswith(('"', "'")) and bit[0] == bit[-1]:
                bit = unescape_string_literal(bit)
            for orm_lookup in orm_lookups:
                or_query |= models.Q((orm_lookup, bit))
        return queryset.filter(or_query)

    def get_queryset(self):
        return self.filter_queryset(super().get_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_search_input_placeholder"] = ", ".join(
            [
                str(self.model._meta.get_field(f).verbose_name)
                for f in self.search_fields
            ]
        )
        return context"""

class DetailMixin(SingleObjectMixin):
    detail_fields = []
    object = None
   
    
    def get_details(self, obj, fields=[]):
        details = OrderedDict()
        for field_name in fields:
            accessor = Accessor(field_name)
            field = accessor.get_field(type(obj))
            if accessor is None:
                continue

            f_value = accessor.resolve(obj)
            if field:
                f_label = field.verbose_name[0].upper() + field.verbose_name[1:]
                f_type = (field.get_internal_type(),)
            else:
                f_type = "method" if callable(f_value) else "property"

            if f_type == "property":
                f_label = ""
            elif f_type == "method":
                f_label = accessor

            details[field_name] = dict(
                name=field_name,
                field_type=f_type,
                label=f_label,
                value=f_value,
            )
        return details

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["details"] = self.get_details(obj, self.detail_fields)
        return context

class PermissionRequiredMixin(DjangoPermissionRequiredMixin):
    permission_required = []  # Define uma lista de permissões personalizadas como predicados
    raise_exception = True
    
    def has_permission(self):
        """
        Verifica se o usuário tem pelo menos uma das permissões de acordo com os predicados fornecidos.
        Cada predicado pode ser uma regra de django-rules.
        """
        if not self.permission_required:
            return True
        
        # Verifica se o usuário possui pelo menos uma das permissões
        for perm in self.permission_required:
            if rules.test_rule(perm, self.request):
                return True
        
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
        
class CustomInlineFormSetFactory(InlineFormSetFactory):
    def construct_formset(self):
        formset_class = self.get_formset_class()
        kwargs = self.get_formset_kwargs()

        # Certificar-se de que 'instance' é um objeto real de modelo e não um OrderedDict
        instance = kwargs.get('instance', None)
        if isinstance(instance, dict):
            instance = instance.get(self.model.__name__.lower())

        # Atualiza os kwargs com a instância correta
        kwargs['instance'] = instance

        return formset_class(**kwargs)

class ActionTabsViewMixin:
    parent = None
    parent_details = []

    def get_parent(self):
        if self.parent:
            return self.parent
        return self.get_object()
    
    def get_parent_details(self):
        parent = self.get_parent()
        details = OrderedDict()
        
        for field_name in self.parent_details:
            field = parent._meta.get_field(field_name)
            value = getattr(parent, field_name, None)
            label = capfirst(field.verbose_name)

            details[field_name] = {
                'name': field_name,
                'label': label,
                'value': value
            }

        return details

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tabs = [
            dict(
                title=getattr(action, "verbose_name", None),
                url=self.urls.get(name),
                action=name,
            )
            for name, action in self.viewset._actions.items()
            if getattr(action, "tab", False)
        ]
        context['parent'] = self.get_parent()
        context['parent_detail'] = self.get_parent_details()
        context['tabs'] = tabs
        return context
