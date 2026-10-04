from django.contrib import admin

from .models import Chamada, CriterioAvaliacao, TipoChamada, TipoChamadaDocumento


class CriterioAvaliacaoInline(admin.TabularInline):
    model = CriterioAvaliacao
    extra = 1


class TipoChamadaDocumentoInline(admin.TabularInline):
    model = TipoChamadaDocumento
    extra = 0


@admin.register(TipoChamada)
class TipoChamadaAdmin(admin.ModelAdmin):
    list_display = ("nome", "evento", "max_autores")
    list_filter = ("evento",)
    search_fields = ("nome",)
    inlines = [TipoChamadaDocumentoInline]


@admin.register(Chamada)
class ChamadaAdmin(admin.ModelAdmin):
    list_display = ("tipo", "etapa", "dt_inicio", "dt_encerramento",
                    "status", "forma_avaliacao", "min_avaliacoes", "min_aprovacoes")
    list_filter = ("tipo__evento", "tipo", "etapa", "status")
    inlines = [CriterioAvaliacaoInline]
