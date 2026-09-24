from django.urls import path

from submissao.views import submissoes_vs, avaliacoes_vs
app_name = "submissao"

urlpatterns = [
    submissoes_vs.url_path, 
    avaliacoes_vs.url_path
]

