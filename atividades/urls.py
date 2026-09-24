from django.urls import path

from .views import (
   atividades_vs,
   tipo_atividades_vs,
   salas_vs,
   agendamento_vs
)

app_name = "atividade"

urlpatterns = [
    atividades_vs.url_path,
    tipo_atividades_vs.url_path,
    salas_vs.url_path,
    agendamento_vs.url_path,
    
]
