from django.contrib import admin
from .models import Documento
# Register your models here.
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("id", "descricao", "tipo")
    list_display_links = (
        "id",
        "descricao",
    )
     
    search_fields = ("descricao","tipo")
    list_filter = ("tipo",)
    inlines = []

admin.site.register(Documento, DocumentoAdmin)