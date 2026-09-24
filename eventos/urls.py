from django.urls import path

from .views import (
    eventos_vs,
    documentos_vs, 
    comissoes_vs, 
    areas_tematicas_vs, 
    parceiros_vs,
    noticias_vs,
    avaliador_vs, 
    itemgaleria_vs

)
app_name = "evento"


urlpatterns = [
    eventos_vs.url_path,
    documentos_vs.url_path,
    comissoes_vs.url_path,
    areas_tematicas_vs.url_path,
    parceiros_vs.url_path,
    noticias_vs.url_path,
    avaliador_vs.url_path,
    itemgaleria_vs.url_path,
]
