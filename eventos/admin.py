from django.contrib import admin

from atividades.models import TipoAtividade
from documentos.forms import DocumentoForm
from documentos.models import Documento
from eventos.forms import  EventoDocumentoForm, EventoForm
from eventos.models import AreaTematica, Avaliador, Comissao, Evento, EventoDocumento, InscricaoEvento, Membro, Monitor

class TipoAtividadeInline(admin.TabularInline):  # ou admin.StackedInline
    model = TipoAtividade
    extra = 1  
    fields = ['nome', 'descricao', 'cor'] 
    readonly_fields = []  
    show_change_link = True 

    def get_queryset(self, request):
        # Exemplo de filtragem opcional
        return super().get_queryset(request)

class AreaTematicaInline(admin.TabularInline):
    model = AreaTematica
    extra = 1  # Número de formulários extras que você deseja exibir
    can_delete = True  # Permite excluir instâncias diretamente no inline
    fields = ['nome', 'descricao', 'cor']
    verbose_name = 'Área Temática'
    verbose_name_plural = 'Áreas Temáticas'

class EventoDocumentoInline(admin.TabularInline):
    model = EventoDocumento
    form = EventoDocumentoForm
    extra = 1  # Número de formulários extras que você deseja exibir
    verbose_name = 'Documento'
    verbose_name_plural = 'Documentos'

# Register your models here.
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "edicao", "ano")
    list_display_links = (
        "id",
        "titulo",
    )
    search_fields = ("titulo","edicao","ano")
    form_class = EventoForm
    inlines = [AreaTematicaInline, TipoAtividadeInline,EventoDocumentoInline]
    

admin.site.register(Evento, EventoAdmin)


class MembroInline(admin.TabularInline):
    model = Membro
    extra = 1  
    can_delete = True 
    fields = ['usuario', 'presidente']
    verbose_name = 'Membro'
    verbose_name_plural = 'Membros'

class ComissaoAdmin(admin.ModelAdmin):
    inlines = [MembroInline]
    list_display = ['nome', 'evento']  # Ajuste conforme os campos do modelo Comissao

admin.site.register(Comissao, ComissaoAdmin)
    


class AvaliadorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'evento']  

admin.site.register(Avaliador,AvaliadorAdmin)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'evento']  

admin.site.register(Monitor,MonitorAdmin)

class InscricaoEventoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "credenciado", "data_inscricao")
    list_display_links = (
        "id",
        "usuario",
    )
    search_fields = ("usuario__nome_completo","evento__titulo")
    fields = ["evento", "usuario", "credenciado", "data_inscricao"]
    inlines = []
 
admin.site.register(InscricaoEvento, InscricaoEventoAdmin)