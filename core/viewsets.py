from types import SimpleNamespace

from django.core.exceptions import ImproperlyConfigured
from django.urls import include, path, reverse
from django.utils.translation import gettext_lazy as _
from django_tables2 import columns
import rules
from simple_menu import MenuItem

from .registries import viewset_registry

ACTIONS_TEMPLATES = {
    "list": dict(
        item=False,
        default=True,
        verbose_name=_("listar"),
        perm="view",
    ),
    "add": dict(
        item=False,
        default=False,
        verbose_name=_("adicionar"),
        icon="fas fa-plus",
        perm="add",
    ),
    "criar": dict(
        item=False,
        default=False,
        verbose_name=_("adicionar"),
        icon="fas fa-plus",
        perm="add",
    ),
    "edit": dict(
        item=True,
        default=False,
        verbose_name=_("alterar"),
        icon="fas fa-pencil",
        order=51,
    ),
    "detail": dict(
        item=True,
        default=False,
        verbose_name=_("detalhes"),
        icon="fas fa-eye",
        order=1,
    ),
    "delete": dict(
        item=True,
        default=False,
        verbose_name=_("excluir"),
        icon="fas fa-trash",
        order=100,
        modal=True
    ),
    "deletar": dict(
        item=True,
        default=False,
        verbose_name=_("excluir"),
        icon="fas fa-trash",
        order=100,
        modal=True
    ),
}


class Action(SimpleNamespace):
    name: str
    verbose_name: str
    item: bool = False
    bulk: bool = False
    default: bool = False
    hidden: bool = False
    route: str = None
    perm: str = None
    icon: str = None
    order: int = None
    css_classes: str = None
    target : str

    def __str__(self) -> str:
        return self.name


class Breadcrumb(SimpleNamespace):
    title: str

    def __str__(self):
        return self.title


class ViewSet:
    title: str = None

    def __init__(self, model=None, name=None, register=True, **kwargs) -> None:
        self.model = model
        if model is not None:
            self.name = self.model._meta.model_name if name is None else name
        else:
            self.name = name
        
        self._actions: dict[str, Action] = {}

        if register:
            viewset_registry.register(self)

        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def action(self, name: str, **kwargs):
        """Add action do viewset

        Arguments:
                name (str): Name of the action
        Keyword arguments:
                verbose_name (str): Name to show in pages
                item (bool): action on the model instance
                batch (bool): action on a set of model instances
                default (bool): Is the default action
                hidden (bool): Action will not show in user interface
                route (str): Text generated on the URL
                perm (str): Permission required to execute the action
                icon (str): Icon to show in the button
                css_classes (str): CSS classes to add to the button
                target (str): Target to open the action
        """

        def decorator(view):
            view_class = type(f"{view.__name__}Action", (WithActionMixin, view), {})
            attrs = {**ACTIONS_TEMPLATES.get(name, {}), **kwargs}
            self._actions[name] = Action(**attrs, name=name, view_class=view_class)
            return view

        return decorator

    def get_url_name(self, action, request=None, namespace=None):
        view_name = []
        if request and request.resolver_match.namespace:
            view_name.append(request.resolver_match.namespace)
        if namespace:
            view_name.append(namespace)
        if self.name:
            view_name.append(f"{self.name}-{action}")
        else:
            view_name.append(action)
        return ":".join(view_name)

    def _urlpatterns(self, prefix=None):
        patterns = []
        for name, action in self._actions.items():
            route_path = []
            if prefix:
                route_path.append(prefix)
            if action.route is None:
                if action.item:
                    route_path.append("<str:pk>")
                if not action.default:
                    route_path.append(name)
            else:
                route_path.append(action.route)

            view_kwargs = {"viewset": self, "action": action}
            if self.model is not None:
                view_kwargs["model"] = self.model

            patterns.append(
                path(
                    "/".join(route_path),
                    action.view_class.as_view(**view_kwargs),
                    name=self.get_url_name(name),
                )
            )
        return patterns

    def get_default_url(self, request=None, namespace=None):
        if self.default_action is not None:
            return reverse(self.get_url_name(self.default_action, request, namespace))
        return ""

    def get_menu_item(self, namespace=None, custom_title=None):
        if custom_title is not None:
            title = custom_title
        elif self.model:
            title = self.model._meta.verbose_name_plural.title()
        else:
            title = self.title
        return MenuItem(
            title,
            url=self.get_default_url(namespace=namespace),
            icon=getattr(self, "menu_icon", None),
            weight=getattr(self, "menu_weight", 1),
        )

    def get_menu_items(self, namespace=None):
        menu_items = []
        for action_name, action in self._actions.items():
            if getattr(action, "menu", False):
                menu_items.append(
                    MenuItem(
                        getattr(action, "verbose_name", action_name),
                        url=reverse(self.get_url_name(action, namespace=namespace)),
                        weight=getattr(action, "menu_weight", 1),
                    )
                )
        return menu_items

    def get_allowed_actions(self, request, **kwargs):
        kwargs.setdefault("hidden", False)
        actions = {}
        for name, action in sorted(
            self._actions.items(), key=lambda i: i[1].order or 99
        ):
            if all(
                [getattr(action, attr, None) == value for attr, value in kwargs.items()]
            ):
                if self.model is not None:
                    meta = self.model._meta
                    if (name == "delete" or name == "add") and not rules.test_rule('is_admin_rule', request):
                        continue
                actions[name] = Action(
                    url=self.get_url_name(name, request),
                    **action.__dict__,
                )
        return actions

    @property
    def url_path(self):
        subpath = f"{self.name}/" if self.name else ""
        return path(subpath, include(self._urlpatterns()))

    @property
    def default_action(self):
        for name, action in self._actions.items():
            if getattr(action, "default", False) and not getattr(action, "item", False):
                return name
        if "list" in self._actions.keys():
            return "list"

    @property
    def default_item_action(self):
        for name, action in self._actions.items():
            if getattr(action, "default", False) and getattr(action, "item", False):
                return name


class WithActionMixin:
    action: Action = None
    viewset: ViewSet = None
    model = None

    @property
    def list_item_url(self):
        action = getattr(self.viewset, "default_item_action", None)
        if action is not None:
            return self.viewset.get_url_name(action, self.request)
        return None

    @property
    def urls(self):
        return {
            action: self.viewset.get_url_name(action, self.request)
            for action, _ in self.viewset._actions.items()
        }

    @property
    def model_meta(self):
        return self.model._meta

    def get_breadcrumbs(self):
        breadcrumbs = []
        # breadcrumbs.append(apps.get_app_config(self.model._meta.app_label).verbose_name)
        if self.model:

            breadcrumbs.append(
                Breadcrumb(
                    title=self.model._meta.verbose_name_plural.title(),
                    url=self.viewset.get_default_url(request=self.request),
                )
            )  # NOQA
        if self.action and not getattr(self.action, "default", False):
            action_title = getattr(self.action, "verbose_name", None) or getattr(
                self.action, "name", None
            )
            breadcrumbs.append(_(action_title).capitalize())

        return breadcrumbs

    def get_table_kwargs(self, **kwargs):
        kwargs = super().get_table_kwargs()
        if "extra_columns" not in kwargs:
            kwargs["extra_columns"] = []
        kwargs["extra_columns"] += [
            
            (
                "actions",
                columns.TemplateColumn(
                    verbose_name="Ação",
                    attrs=dict(
                        th={"class": "text-end w-150px"},
                        td={"class": "text-end", "style": "width: 150px"},
                    ),
                    orderable=False,
                    template_name="includes/list_item_actions.html",
                    extra_context={
                        "actions": self.viewset.get_allowed_actions(
                            self.request, item=True
                        )
                    },
                    exclude_from_export=True,
                ),
            ),
        ]
        return kwargs

    def get_table_class(self):
        table_class = super().get_table_class()
        table_class._meta.sequence = ["...", "actions"]
        return table_class

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"breadcrumbs": self.get_breadcrumbs(), "viewset": self.viewset})
        return context

    def get_success_url(self):
        try:
            return super().get_success_url()
        except ImproperlyConfigured:
            return reverse(
                self.viewset.get_url_name(self.viewset.default_action, self.request)
            )

    @property
    def list_actions(self):
        allowed_actions = self.viewset.get_allowed_actions(
            self.request, item=False, default=False, bulk=False
        )
        return {k: v for k, v in allowed_actions.items() if k != self.action.name}

    @property
    def bulk_actions(self):
        return self.viewset.get_allowed_actions(self.request, item=False, bulk=True)
