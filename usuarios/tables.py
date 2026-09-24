from django.urls import reverse
import django_tables2 as tables

from atividades.models import Atividade, InscricaoAtividade, StatusAtividade
from chamadas.models import StatusChamada
from django.utils.html import format_html

from submissao.models import Avaliacao, StatusAvaliacao, StatusTrabalho, Trabalho


class MinhasInscricoesAtividadeTable(tables.Table):
    tipo_atividade = tables.Column(accessor="atividade__tipo", verbose_name="Tipo")
    atividade = tables.Column(accessor="atividade__titulo", verbose_name="Atividade")
    dt_inicio = tables.Column(accessor="inicio", verbose_name="Início")
    local = tables.Column(accessor="local", verbose_name="Local")
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=()) 

    class Meta:
        model = InscricaoAtividade
        fields = (
            "tipo_atividade",
            "atividade",
            "dt_inicio",
            "local",
        )
    
    def render_actions(self, record):
        delete_url = reverse("user:inscricaoatividade-delete", args=[record.id])
        return format_html(
                (
                   
                    '<a title="Cancelar Inscrição" class="btn btn-light btn-link text-black action-delete px-2 py-2 ms-1"" '
                    'hx-get="{}" hx-target="#app-modal" hx-trigger="click" data-bs-toggle="modal" data-bs-target="#app-modal"' 
                    'href="{}">'
                    '<i class="fas fa-trash"></i></a>'
                ),
                delete_url,
                delete_url,
            )
        
class AtividadeInscricaoTable(tables.Table):
    tipo = tables.Column(accessor="tipo", verbose_name="Tipo")
    titulo = tables.Column(accessor="titulo", verbose_name="Atividade")
    duracao = tables.Column(accessor="duracao", verbose_name="Duranção")
    periodo_inscricao = tables.Column(accessor="inicio_inscricoes", verbose_name="Periondo de Inscrição")
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())
    class Meta:
        model = Atividade
        fields = (
            "tipo",
            "titulo",
            "duracao",
            "periodo_inscricao",
            "status",
            "actions"
        )
    def render_periodo_inscricao(self, record):
        return format_html(
               str(record.inicio_inscricoes) + " a " + str(record.fim_inscricoes)
        )
            
         
    def render_actions(self, record):
        detail_url = reverse("user:atividade-detail", args=[record.id])
        inscrever_url = reverse("user:atividade-inscreverse", args=[record.id])
        if record.status == StatusAtividade.INSCRICOES_ABERTAS:
          return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2"'
                    'hx-get="{}" hx-target="#app-modal" hx-trigger="click" data-bs-toggle="modal" data-bs-target="#app-modal"' 
                    'href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Inscrever-se" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" '
                    'hx-get="{}" hx-target="#app-modal" hx-trigger="click" data-bs-toggle="modal" data-bs-target="#app-modal"' 
                    'href="{}">'
                    '<i class="fas fa-check"></i></a>'
                ),
                detail_url,
                detail_url,
                inscrever_url,
                inscrever_url,
            )
        else:
            return format_html(
                 (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                ),
                detail_url,
            )
    

class MeusTrabalhosTable(tables.Table):
    autores_string = tables.Column(accessor='autores_string', verbose_name='Autores')
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = Trabalho
        fields = ['tipo_chamada', 'titulo', 'autores_string', 'status', 'actions']
    
    def render_status(self, record):
        if record.tipo_chamada.chamada_atual.status == StatusChamada.ABERTO and record.status in [StatusTrabalho.APROVADO, StatusTrabalho.REPROVADO, StatusTrabalho.N_APRESENTADO]:
            return format_html(
                'Em avaliação'
            )
        else:
            return format_html(
               record.get_status_display()
            )
            
         
    def render_actions(self, record):
        detail_url = reverse("user:trabalho-detail", args=[record.id])
        edit_url = reverse("user:trabalho-edit", args=[record.id])
        deletar_url = reverse("user:trabalho-deletar", args=[record.id])
        cancelar_url = reverse("user:trabalho-cancelar_submissao", args=[record.id])
        if record.status == StatusTrabalho.RASCUNHO and record.tipo_chamada.primeira_chamada.status == StatusChamada.ABERTO :
            return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                    '<a title="Excluir" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" '
                    'hx-get="{}" hx-target="#app-modal" hx-trigger="click" data-bs-toggle="modal"'
                    'data-bs-target="#app-modal" href="{}"><i class="fas fa-trash"></i></a>'
                ),
                detail_url,
                edit_url,
                deletar_url,
                deletar_url,
            )
        elif record.tipo_chamada.primeira_chamada.status == StatusChamada.ABERTO and record.status == StatusTrabalho.SUBMETIDO:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Cancelar Submissão" class="btn btn-light btn-link text-black action-detail px-2 py-2 ml-1" href="{}">'
                    '<i class="fas fa-xmark"></i></a>'
                ),
                detail_url,
                cancelar_url

            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                
                ),
                detail_url,
                )

             
class MinhasAvaliacoesTable(tables.Table):
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())
    
    class Meta:
        model = Avaliacao
        fields = ['submissao__trabalho__titulo', 'submissao__chamada', 'status', 'nota_parcial', 'actions']
    
    def render_actions(self, record):

        edit_url = reverse("user:avaliacao-edit", args=[record.id])
        detail_url = reverse("user:avaliacao-detail", args=[record.id])
        aceitar_url = reverse("user:avaliacao-aceitar_avaliacao", args=[record.id])
        cancelar_url = reverse("user:avaliacao-cancelar_avaliacao", args=[record.id])
        
        if record.status == StatusAvaliacao.AVALIACAO_SOLICITADA:
            return format_html(
                (
                    '<a title="Aceitar Avaliar" class="btn btn-light btn-link text-black action-avaliar px-2 py-2" href="{}">'
                    '<i class="fas fa-check"></i>'
                    '</a><br/>'
                    '<small class="small">Aceitar até: {}</small>'
                ),
                aceitar_url,
                record.dt_limite_aceite.strftime("%d/%m")
            )
        elif record.status == StatusAvaliacao.EM_AVALIACAO:
                return format_html(
                (
                    
                    '<a title="Cancelar Avaliação" class="btn btn-light btn-link text-black action-detail px-2 py-2 mr-1" href="{}">'
                    '<i class="fas fa-xmark"></i></a>'
                    '<a title="Editar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
            
                cancelar_url,
                edit_url,

            )
        else:
            return format_html(
                '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>',
                    detail_url
            )
        