from django.contrib import admin

from submissao.models import Trabalho,Avaliacao,AvaliacaoCriterio, Submissao
class TrabalhoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "autor_principal", "status", "area_tematica")
    list_display_links = (
        "id",
        "titulo",
    )
    search_fields = ("titulo","autor_principal__email")
    list_filter = ("status", "area_tematica", "tipo_chamada")
    inlines = []
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "titulo",
                    "autor_principal",
                    "coautores",
                    "area_tematica",
                    "resumo",
                    "palavras_chave",
                    "descricao",
                    "status",
                )
            },
        ),
    )
admin.site.register(Trabalho, TrabalhoAdmin)

class SubmissaoAdmin(admin.ModelAdmin):
    list_display = ("id", "trabalho", "chamada", "status_avaliacao", "criado_em")
    list_display_links = (
        "id",
        "trabalho",
    )
    search_fields = ("trabalho__titulo",)
    list_filter = ("status_avaliacao","chamada__etapa", "chamada__status")
    inlines = []
    
admin.site.register(Submissao, SubmissaoAdmin)

class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "submissao", "avaliador", "status")
    list_display_links = (
        "id",
        "submissao",
    )
     
    search_fields = ("submissao__trabalho__titulo","avaliador__email")
    list_filter = ("status", "submissao__chamada__etapa","submissao__chamada__tipo")
    inlines = []
    
admin.site.register(Avaliacao, AvaliacaoAdmin)

class AvaliacaoCriterioAdmin(admin.ModelAdmin):
    list_display = ("id", "avaliacao", "criterio")
    list_display_links = (
        "id",
    )
     
    search_fields = ("avaliacao__avaliador__email", "avaliacao__submissao__trabalho__titulo")
    list_filter = ("avaliacao__submissao__chamada__etapa","avaliacao__submissao__chamada__tipo")
    inlines = []
    
admin.site.register(AvaliacaoCriterio, AvaliacaoCriterioAdmin)