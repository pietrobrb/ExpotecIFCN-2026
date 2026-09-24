from django.urls import path

from .views import AtividadesEventoView, portal_vs, PortalEventoView

app_name = "portal"

urlpatterns = [
    path('', PortalEventoView.as_view(), name='index'),
    path('evento/agenda/<int:dia>', AtividadesEventoView.as_view(), name='evento-list_dia'),
]
urlpatterns += [portal_vs.url_path,]
