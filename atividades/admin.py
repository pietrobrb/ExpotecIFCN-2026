from django.contrib import admin

from atividades.models import Agendamento, Atividade, InscricaoAtividade, TipoAtividade

# Register your models here.

class TipoAtividadeAdmin(admin.ModelAdmin):
    list_display = ("id", "evento", "nome")
    list_display_links = (
        "id",
        "nome",
    )
    search_fields = ("titulo","edicao","ano")
    fields = ['evento', 'nome', 'descricao', 'cor', 'icone']
    inlines = []
    

admin.site.register(TipoAtividade, TipoAtividadeAdmin)

class AtividadeAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "titulo", "status")
    list_display_links = (
        "id",
        "titulo",
    )
    search_fields = ("tipo__nome","titulo")
    fields = [
        'tipo'
        'titulo', 
        'descricao', 
        'vagas_limitadas', 
        'qtd_vagas', 
        'inicio_inscricoes', 
        'fim_inscricoes', 
        'duracao', 
        'status', 
    ]
    inlines = []
 
admin.site.register(Atividade, AtividadeAdmin)

class InscricaoAtividadeAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "atividade", "data_inscricao")
    list_display_links = (
        "id",
        "usuario",
    )
    search_fields = ("usuario__nome_completo","atividade__titulo")
    fields = ["atividade", "usuario", "presente", "data_inscricao"]
    inlines = []
     
 
admin.site.register(InscricaoAtividade, InscricaoAtividadeAdmin)


class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "sala", "atividade", "dia", "inicio", "fim")
    list_display_links = (
        "id",
        "sala",
    )
    search_fields = ("atividade__titulo","sala__nome")
    fields = [
        'sala',"atividade", "dia", "inicio", "fim"
    ]
    inlines = []
admin.site.register(Agendamento, AgendamentoAdmin)