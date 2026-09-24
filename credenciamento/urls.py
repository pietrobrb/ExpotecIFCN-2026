from django.urls import path

from .views import (
   credenciamento_vs,
   presenca_vs
)

app_name = "credenciamento"


urlpatterns = [
    credenciamento_vs.url_path,
    presenca_vs.url_path, 
]