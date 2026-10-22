from django.urls import path
from django.views.generic import TemplateView

from .views import (
    AtividadesEventoView,
    PortalEventoView,
    agenda_json,
    portal_vs,
)

app_name = "portal"

urlpatterns = [
    path("", PortalEventoView.as_view(), name="index"),
    # Programação: começa pelo primeiro dia do evento.
    path(
        "programacao/",
        AtividadesEventoView.as_view(),
        {"dia": 1},
        name="programacao",
    ),
    # Mantém a rota anterior de programação por dia.
    path(
        "evento/agenda/<int:dia>",
        AtividadesEventoView.as_view(),
        name="evento-list_dia",
    ),
    # Páginas públicas do novo site.
    path(
        "sobre/",
        TemplateView.as_view(template_name="sobre.html"),
        name="sobre",
    ),
    path(
        "mapa/",
        TemplateView.as_view(template_name="mapa.html"),
        name="mapa",
    ),
    path(
        "frequencia/",
        TemplateView.as_view(template_name="frequencia.html"),
        name="frequencia",
    ),
    path(
        "minha-agenda/",
        TemplateView.as_view(template_name="minha_agenda.html"),
        name="minha_agenda",
    ),
    path(
        "api/minha-agenda/",
        agenda_json,
        name="agenda_json",
    ),
]

urlpatterns += [portal_vs.url_path]
