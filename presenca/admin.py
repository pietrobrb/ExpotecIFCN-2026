from django.contrib import admin

from .models import RegistroPresenca, SessaoPresenca


@admin.register(SessaoPresenca)
class SessaoPresencaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "agendamento",
        "monitor",
        "status",
        "inicio",
        "fim",
        "token_expira_em",
    )

    list_filter = ("status",)

    search_fields = (
        "agendamento__atividade__titulo",
        "monitor__usuario__nome_completo",
    )

    readonly_fields = (
        "token_atual",
        "criado_em",
        "atualizado_em",
    )


@admin.register(RegistroPresenca)
class RegistroPresencaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sessao",
        "inscricao",
        "registrado_em",
    )

    list_filter = ("registrado_em",)

    search_fields = (
        "inscricao__usuario__nome_completo",
        "inscricao__atividade__titulo",
    )

    readonly_fields = ("registrado_em",)
