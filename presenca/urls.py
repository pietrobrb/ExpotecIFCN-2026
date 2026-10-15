from django.urls import path

from . import views

app_name = "presenca"

urlpatterns = [
    path(
        "monitor/",
        views.monitor,
        name="monitor",
    ),
    path(
        "monitor/<int:agendamento_id>/abrir/",
        views.abrir_presenca,
        name="abrir_presenca",
    ),
    path(
        "monitor/sessao/<int:sessao_id>/",
        views.controle_sessao,
        name="controle_sessao",
    ),
    path(
        "monitor/sessao/<int:sessao_id>/estado/",
        views.estado_sessao,
        name="estado_sessao",
    ),
    path(
        "checkin/<uuid:token>/",
        views.checkin,
        name="checkin",
    ),
    path(
        "monitor/sessao/<int:sessao_id>/renovar/",
        views.renovar_presenca,
        name="renovar_presenca",
    ),
    path(
        "monitor/sessao/<int:sessao_id>/encerrar/",
        views.encerrar_presenca,
        name="encerrar_presenca",
    ),
    path(
        "monitor/sessao/<int:sessao_id>/iniciar/",
        views.iniciar_atividade,
        name="iniciar_atividade",
    ),
]
