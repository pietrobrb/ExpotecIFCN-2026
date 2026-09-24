from django.urls import reverse
import django_tables2 as tables
from django.utils.html import format_html

from atividades.models import TipoAtividade
from eventos.models import AreaTematica, Avaliador, Comissao, EventoDocumento, ItemGaleria, Noticia

class EventoAreaTematicaTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    nome = tables.Column(accessor="nome", verbose_name="Nome", orderable=True)
    cor = tables.Column(accessor="cor", verbose_name="Cor", orderable=True)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = AreaTematica
        fields = (
            "id",
            "nome",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("evento:areatematica-detail", args=[record.id])
        edit_url = reverse("evento:areatematica-edit", args=[record.id])
        delete_url = reverse("evento:areatematica-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )

class EventoTipoAtividadeTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    nome = tables.Column(accessor="nome", verbose_name="Nome", orderable=True)
    cor = tables.Column(accessor="cor", verbose_name="Cor", orderable=True)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = TipoAtividade
        fields = (
            "id",
            "nome",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("atividade:tipoatividade-detail", args=[record.id])
        edit_url = reverse("atividade:tipoatividade-edit", args=[record.id])
        delete_url = reverse("atividade:tipoatividade-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )
        
class EventoDocumentoTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    descricao = tables.Column(accessor="documento__descricao", verbose_name="Descricao", orderable=True)
    tipo = tables.Column(accessor="documento__tipo", verbose_name="Tipo", orderable=True)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = EventoDocumento
        fields = (
            "id",
            "descricao",
            "tipo",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("evento:eventodocumento-view", args=[record.id])
        edit_url = reverse("evento:eventodocumento-edit", args=[record.id])
        delete_url = reverse("evento:eventodocumento-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )

        
class EventoComissaoTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    nome = tables.Column(accessor="nome", verbose_name="Nome", orderable=True)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = Comissao
        fields = (
            "id",
            "nome",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("evento:comissao-detail", args=[record.id])
        edit_url = reverse("evento:comissao-edit", args=[record.id])
        delete_url = reverse("evento:comissao-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )

   
class EventoParceiroTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    nome = tables.Column(accessor="nome", verbose_name="Nome", orderable=True)
    url = tables.Column(accessor="url", verbose_name="URL", orderable=False)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = Comissao
        fields = (
            "id",
            "nome",
            "url",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("evento:parceiro-detail", args=[record.id])
        edit_url = reverse("evento:parceiro-edit", args=[record.id])
        delete_url = reverse("evento:parceiro-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )

class EventoItemGaleriaTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    titulo = tables.Column(accessor="titulo", verbose_name="título", orderable=True)
    url = tables.Column(accessor="url", verbose_name="URL", orderable=False)
    #img = tables.Column(accessor="img", verbose_name="Imagem da ODS" )
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = ItemGaleria
        fields = (
            "id",
            "titulo",
            "url",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("evento:itemgaleria-detail", args=[record.id])
        edit_url = reverse("evento:itemgaleria-edit", args=[record.id])
        delete_url = reverse("evento:itemgaleria-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )


class EventoNoticiaTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    titulo = tables.Column(accessor="titulo", verbose_name="Título", orderable=True)
    subtitulo = tables.Column(accessor="subtitulo", verbose_name="Subtítulo", orderable=True)
    ordem = tables.Column(accessor="ordem", verbose_name="Ordem", orderable=True)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = Noticia
        fields = (
            "id",
            "titulo",
            "subtitulo",
            "ordem",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("evento:noticia-detail", args=[record.id])
        edit_url = reverse("evento:noticia-edit", args=[record.id])
        delete_url = reverse("evento:noticia-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )

class EventoTipoChamadaTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    nome = tables.Column(accessor="nome", verbose_name="Nome", orderable=True)
    max_autores = tables.Column(accessor="max_autores", verbose_name="Max. Autores", orderable=False)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = Noticia
        fields = (
            "id",
            "nome",
            "max_autores",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("chamada:tipochamada-detail", args=[record.id])
        edit_url = reverse("chamada:tipochamada-edit", args=[record.id])
        delete_url = reverse("chamada:tipochamada-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )


class EventoSalaTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    nome = tables.Column(accessor="nome", verbose_name="Nome", orderable=True)
    capacidade = tables.Column(accessor="capacidade", verbose_name="Capacidade", orderable=True)
    actions = tables.Column(verbose_name="Ações", orderable=False, empty_values=())

    class Meta:
        model = Noticia
        fields = (
            "id",
            "nome",
            "capacidade",
            "actions"
        )
   

    def render_actions(self, record):
        detail_url = reverse("atividade:sala-detail", args=[record.id])
        edit_url = reverse("atividade:sala-edit", args=[record.id])
        delete_url = reverse("atividade:sala-delete", args=[record.id])
        if self.request.user.is_superuser or (self.request.user.is_authenticated and self.request.evento.comissoes.all().filter(membros__usuario = self.request.user, membros__presidente=True).exists()):
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
                delete_url,
                delete_url,
            )
        else:
                return format_html(
                (
                    '<a title="Detalhar" class="btn btn-light btn-link text-black action-detail px-2 py-2" href="{}">'
                    '<i class="fas fa-eye"></i></a>'
                    '<a title="Alterar" class="btn btn-light btn-link text-black action-detail px-2 py-2 ms-1"" href="{}">'
                    '<i class="fas fa-pencil"></i></a>'
                ),
                detail_url,
                edit_url,
            )


class EventoAvaliadoresTable(tables.Table):
    id = tables.Column(accessor="id", verbose_name="Id", orderable=True)
    email = tables.Column(accessor="usuario__email", verbose_name="Email do Usuário", orderable=True)
    areas = tables.Column(accessor="areas_tematicas", verbose_name="Área", orderable=True)
    avaliacoes = tables.Column(accessor="avaliacoes", verbose_name="Num. Avaliações", orderable=True)
   
    class Meta:
        model = Avaliador
        fields = (
            "id",
            "email",
            "areas",
            "avaliacoes",
   
        )

    def render_avaliacoes(self, record):
        return record.avaliacoes.count()
    
    def render_areas(self, record):
        return ', '.join([area.nome for area in record.areas_tematicas.all()])
    
    def render_actions(self, record):
         return ''
