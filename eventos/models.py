from collections import defaultdict
from django.db import models,transaction

from core.fields import FormatStringFileUpload, get_current_year_str
from django.utils.translation import gettext_lazy as _

from documentos.models import Documento, TipoDocumento
from enderecos.models import Contato, Endereco
from usuarios.models import User
from datetime import timedelta
from django.db.models import Q, Min
class Evento(models.Model):
    titulo = models.CharField(
        max_length=50,
        verbose_name=_("Título")
    )
    subtitulo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Subtítulo")
    )
    edicao = models.CharField(
        max_length=50,
        verbose_name=_("Edição")
    )
    ano = models.CharField(
        max_length=4,
        default=get_current_year_str,
        verbose_name=_("Ano")
    )
    dt_inicio = models.DateField(
        verbose_name=_("Início")
    )
    dt_encerramento = models.DateField(
        verbose_name=_("Encerramento")
    )
    apresentacao = models.TextField(
        verbose_name=_("Texto de Apresentação"),
        blank=True,
        null=True,
    )
    instagram = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Instagram")
    )
    youtube = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Youtube")
    )
    logo = models.ImageField(
        upload_to=FormatStringFileUpload("eventos/logo/{instance.id}/{filename}"),
        blank=True,
        null=True,
        verbose_name=_("Logo")
    )
    logo_mini = models.ImageField(
        upload_to=FormatStringFileUpload("eventos/logo/{instance.id}/{filename}"),
        blank=True,
        null=True,
        verbose_name=_("Mini Logo")
    )
    imagem_promocional = models.ImageField(
        upload_to=FormatStringFileUpload("eventos/imagem/{instance.id}/{filename}"),
        blank=True,
        null=True,
        verbose_name=_("Imagem Promocional")
    )
    video_promocional = models.FileField(
        upload_to=FormatStringFileUpload("eventos/video/{instance.id}/{filename}"),
        blank=True,
        null=True,
        verbose_name=_("Video Promocional")
    )
    ch_total = models.PositiveIntegerField(
        verbose_name=_("CH Total")
    )
    ch_min_certificado = models.PositiveIntegerField(
        verbose_name=_("CH Mínima para Certificado"),
        blank=True,
        null=True,
    )
    
    endereco = models.ForeignKey(
        Endereco,
        related_name='eventos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Endereço")
    )
    
    contatos = models.ManyToManyField(
        Contato,
        through='EventoContato',
        related_name='eventos',
        verbose_name=_("Contatos")
    )

    def __str__(self):
        return f"{self.edicao} - {self.titulo}"
    
    @property
    def downloads(self):
        return self.evento_documentos.filter(documento__tipo=TipoDocumento.DOWNLOAD, documento__file__isnull=False)
    
    @property
    def regras(self):
        return self.evento_documentos.filter(documento__tipo=TipoDocumento.REGRA, documento__file__isnull=False)
    
    @property
    def atividades(self):
        from atividades.models import Atividade
        atividades = Atividade.objects.filter(
            tipo__evento=self
        ).annotate(
            inicio=Min('agendamentos__dia')
        ).filter(
            Q(inicio__isnull=True) | Q(inicio__gte=self.dt_inicio)
        ).order_by('inicio', 'tipo') 
        return atividades.distinct()
    
    @property
    def usuarios_inscritos(self):
        return self.inscricoes.values_list('usuario', flat=True)
    
    @property
    def usuarios_membros(self):
        membros = [ m.usuario for c in self.comissoes.all() for m in c.membros.filter(presidente = False) ]
        return membros
    
    @property
    def usuarios_presidentes(self):
        presidedentes = [ m.usuario for c in self.comissoes.all() for m in c.membros.filter(presidente = True) ]
        return presidedentes
    
    @property
    def top5_noticias(self):
        return self.noticias.order_by('ordem')[:5] 
    
    
    @property
    def dias_do_evento(self):
        return [self.dt_inicio + timedelta(days=x) for x in range((self.dt_encerramento - self.dt_inicio).days + 1)]
    
    @property
    def agenda_evento(self):
        tipos_atividade = self.tipos_de_atividade.prefetch_related('atividades__agendamentos')
        # Coleta todos os agendamentos das atividades
        agendamentos = []
        for tipo in tipos_atividade:
            for atividade in tipo.atividades.all():
                agendamentos.extend(atividade.agendamentos.all())

        agendamentos_por_dia = []
        # Organiza os agendamentos por dia
        
        for dia in self.dias_do_evento:
            dia_str = dia.strftime("%Y-%m-%d")
            agendamentos_do_dia = [
                agendamento for agendamento in agendamentos
                if agendamento.dia.strftime("%Y-%m-%d") == dia_str 
            ]
            agendamentos_por_dia.append(agendamentos_do_dia)
        return agendamentos_por_dia
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'



class AreaTematica(models.Model):
    evento = models.ForeignKey(
        Evento,
        related_name='areas_tematicas',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )
    nome = models.CharField(
        max_length=50,
        verbose_name=_("Nome")
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Descrição")
    )
    cor = models.CharField(
        max_length=20, 
        verbose_name=_("Cor"),
        blank=True,
        null=True,
    )

    icone = models.CharField(
        max_length=100, 
        verbose_name=_("Ícone"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Área Temática'
        verbose_name_plural = 'Áreas Temáticas'


class Comissao(models.Model):
    evento = models.ForeignKey(
        Evento,
        related_name='comissoes',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )
    nome = models.CharField(
        max_length=200,
        verbose_name=_("Nome")
    )

    class Meta:
        verbose_name = 'Comissão'
        verbose_name_plural = 'Comissões'

    def __str__(self):
        return self.nome


class Membro(models.Model):
    comissao = models.ForeignKey(
        Comissao,
        related_name='membros',
        on_delete=models.CASCADE,
        verbose_name=_("Comissão")
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Usuário")
    )
    presidente = models.BooleanField(
        default=False,
        verbose_name=_("Presidente")
    )

    class Meta:
        verbose_name = 'Membro de Comissão'
        verbose_name_plural = 'Membros de Comissões'
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.comissao.nome}"


class Avaliador(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Usuário")
    )
    evento = models.ForeignKey(
        Evento,
        related_name='avaliadores',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )
    areas_tematicas = models.ManyToManyField(
        AreaTematica,
        related_name='avaliadores',
        verbose_name=_("Áreas Temáticas de Interesse")
    )

    class Meta:
        verbose_name = 'Avaliador'
        verbose_name_plural = 'Avaliadores'
    
    def __str__(self):
        return f"{self.usuario.email}"
    
    @property
    def areas(self):
        return ', '.join([area.nome for area in self.areas_tematicas.all()])


    @property
    def qtd_avaliacoes(self):
        return self.avaliacoes.count()
    
    


class Noticia(models.Model):
    evento = models.ForeignKey(
        Evento,
        related_name='noticias',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name=_("Título")
    )
    subtitulo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Subtítulo")
    )
    poster = models.ImageField(
        upload_to=FormatStringFileUpload('noticias/posters/{instance.id}/{filename}'),
        verbose_name=_("Pôster"),
        default='img/placeholders/default_poster.jpg'
    )
    thumbnail = models.ImageField(
        upload_to=FormatStringFileUpload("noticias/thumbnails/{instance.id}/{filename}"),
        blank=True,
        null=True,
        verbose_name=_("Thumbnail")
    )
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("URL")
    )
    texto = models.TextField(
        verbose_name=_("Texto")
    )
    ordem = models.PositiveIntegerField(
        verbose_name=_("Ordem"),
        default= 0
    )

    dt_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Cadastro"),
        null=True
    )

    def save(self, *args, **kwargs):
        if self.ordem == 0:
            self.ordem = Noticia.objects.filter(evento=self.evento).count() + 1
        super().save(*args, **kwargs)
        with transaction.atomic():
            if Noticia.objects.filter(evento=self.evento, ordem=self.ordem).exists():
                conflicting = (
                    Noticia.objects.filter(evento=self.evento, ordem=self.ordem)
                    .exclude(pk=self.pk)
                    .first()
                )
                if conflicting:
                    conflicting.ordem += 1
                    conflicting.save()


    class Meta:
        ordering = ['ordem']
        verbose_name = _("Notícia")
        verbose_name_plural = _("Notícias")

    def __str__(self):
        return self.titulo


class EventoDocumento(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='evento_documentos',
        verbose_name=_("Evento")
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='evento_documentos',
        verbose_name=_("Documento")
    )

    class Meta:
        unique_together = ('evento', 'documento') 
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
    
    def __str__(self) -> str:
        return f'{self.evento.titulo} - {self.documento}'


class Parceiro(models.Model):
    evento = models.ForeignKey(
        Evento,
        related_name='parceiros',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )
    nome = models.CharField(
        max_length=200,
        verbose_name=_("Nome")
    )
    logo = models.ImageField(
        upload_to=FormatStringFileUpload("eventos/parceiros/{instance.id}/{filename}"),
        verbose_name=_("Logo"),
        default='img/placeholders/default_logo.jpg'
    )
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("URL")
    )

    class Meta:
        verbose_name = _("Parceiro")
        verbose_name_plural = _("Parceiros")

    def __str__(self):
        return self.nome


class ItemGaleria(models.Model):
    titulo = models.CharField(
        max_length=200,
        verbose_name=_("Nome")
    )
    img = models.ImageField(
        upload_to=FormatStringFileUpload("eventos/item/galeria/{filename}"),
        verbose_name=_("Logo"),
        default='img/placeholders/default_logo.jpg'
    )
    url = models.URLField(
        null=True,
        verbose_name=_("URL")
    )
    evento = models.ForeignKey(
        Evento,
        related_name='ItemGaleria',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )

    class Meta:
        verbose_name = _("ItemGaleria")
        verbose_name_plural = _("ItensGaleria")

    def __str__(self):
        return self.titulo

class EventoContato(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='evento_contatos')
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='contato_eventos')

    def __str__(self):
        return f"{self.contato.nome} - {self.evento.titulo}"

    class Meta:
        verbose_name = "Contato do Evento"
        verbose_name_plural = "Contatos do Evento"

class InscricaoEvento(models.Model):
    evento = models.ForeignKey(
        Evento,
        related_name='inscricoes',
        on_delete=models.CASCADE,
        verbose_name="Evento"
    )
    usuario = models.ForeignKey(
        User,
        related_name='inscricoes_eventos',
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )
    credenciado = models.BooleanField(
        default=False,
        verbose_name="Credenciado"
    )
    data_inscricao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Inscrição"
    )

    def __str__(self):
        return f"{self.usuario} - {self.evento} (Credenciado: {self.credenciado})"
    
    class Meta:
        verbose_name = "Inscrição em Evento"
        verbose_name_plural = "Inscrições em Eventos"
        unique_together = ('evento', 'usuario')


class Monitor(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Usuário")
    )
    evento = models.ForeignKey(
        Evento,
        related_name='monitores',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )

    ira = models.DecimalField(default=0, decimal_places=2, verbose_name=_("IRA"), max_digits=5)
    
    ano = models.PositiveIntegerField(default=1, verbose_name=_("Ano do Curso"))
    
    selecionado = models.BooleanField(default=False, verbose_name=_("Foi Selecionado?"))

    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Descrição")
    )

    class Meta:
        verbose_name = 'Monitor'
        verbose_name_plural = 'Monitores'
    
    def __str__(self):
        return f"{self.usuario.email}"
    