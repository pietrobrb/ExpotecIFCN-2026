from django.urls import path

from .views import chamadas_vs , tipo_chamadas_vs

app_name = "chamada"

urlpatterns = [
    chamadas_vs.url_path,
    tipo_chamadas_vs.url_path
]

