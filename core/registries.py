from django.apps import apps
from django.urls import include, path
from persisting_theory import Registry


class ViewSetRegistry(Registry):
    look_into = "views"

    def autodiscover(self, force_reload=False):
        app_names = [
            app_config.name
            for app_config in apps.get_app_configs()
            if app_config.name != "core"
        ]
        return super().autodiscover(app_names, force_reload)

    def get_object_name(self, data):
        if hasattr(data, "name"):
            return data.name
        return super().get_object_name(data)

    def _urlpatterns(self):
        urls = []
        for vs in self.values():
            prefix = ""
            if vs.name:
                prefix = f"{vs.name}/"
            if vs.model:
                prefix = f"{vs.model._meta.app_label}/{vs.model._meta.model_name}/"
            urls.append(path(prefix, include(vs._urlpatterns())))
        return urls

    def get_urls(self, namespace=None):
        """URLs from vregistred viewsets with specified namespace"""
        return (self._urlpatterns(), "viewsets", namespace)

    @property
    def urls(self):
        """URLs from registred viewsets with default namespace"""
        return self.get_urls()


viewset_registry = ViewSetRegistry()
