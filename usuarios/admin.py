from django.contrib import admin
from .models import User
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "nome_completo", "cpf", "vinculo")
    list_display_links = (
        "id",
        "email",
    )
    search_fields = ("username","cpf")
    list_filter = ("vinculo",)
    inlines = []

admin.site.register(User, UsuarioAdmin)