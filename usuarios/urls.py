from django.urls import path
from usuarios.views import IndexView, MeuCadastroMonitorAddView, MeuCadastroMonitorEditView,MeuPerfilEditView,DashboardView,MinhasInscricoesView,InscreverseView,MeuCadastroAvaliadorEditView,MeuCadastroAvaliadorAddView
from usuarios.views import trabalhos_vs, avaliacoes_vs, dashboard_vs, atividades_vs, insc_atividades_vs
app_name = "user"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("me/", MeuPerfilEditView.as_view(), name="meu_perfil"),
    path("me/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("me/inscricoes/", MinhasInscricoesView.as_view(), name="minhas_inscricoes"),
    path('me/inscricaoevento/', InscreverseView.as_view(), name='inscreverse'),
    path("me/avaliador/edit", MeuCadastroAvaliadorEditView.as_view(), name="edit_avaliador"),
    path("me/avaliador/add", MeuCadastroAvaliadorAddView.as_view(), name="add_avaliador"),
    path("me/monitor/add", MeuCadastroMonitorAddView.as_view(), name="add_monitor"),
    path("me/monitor/edit", MeuCadastroMonitorEditView.as_view(), name="edit_monitor"),
    trabalhos_vs.url_path,
    avaliacoes_vs.url_path,
    dashboard_vs.url_path,
    atividades_vs.url_path,
    insc_atividades_vs.url_path
]
