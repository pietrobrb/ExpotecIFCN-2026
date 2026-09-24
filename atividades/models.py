from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import time

from core.models import get_hoje
from eventos.models import Evento
from usuarios.models import User
from django.utils import timezone

from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
class TipoAtividade(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='tipos_de_atividade',
        verbose_name=_("Evento")
    )

    nome = models.CharField(
        max_length=30,
        verbose_name=_("Nome")
    )

    descricao = models.CharField(
        max_length=100,
        verbose_name=_("Descrição"),
        null=True,
        blank=True

    )

    cor = models.CharField(
        max_length=20, 
        verbose_name=_("Cor")
    )

    icone = models.CharField(
        max_length=50, 
        verbose_name=_("Ícone"),
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Tipo de Atividade'
        verbose_name_plural = 'Tipos de Atividade'

class StatusAtividade(models.TextChoices):
    INSCRICOES_ABERTAS = 'inscricoes_abertas', _("Inscrições Abertas")
    INSCRICOES_ENCERRADAS = 'inscricoes_encerradas', _("Inscrições Encerradas")
    SEM_VAGA = 'sem_vaga', _("Sem Vaga")
    INSCRICOES_EMBREVE = 'inscricoes_embreve', _("Inscrições Em Breve")
    RASCUNHO = 'rascunho', _("Rascunho")

class Atividade(models.Model):
    tipo = models.ForeignKey(
        TipoAtividade,
        on_delete=models.CASCADE,
        related_name='atividades',
        verbose_name=_("Tipo de Atividade")
    )

    titulo = models.CharField(
        max_length=255,
        verbose_name=_("Título")
    )

    descricao = models.TextField(
        verbose_name=_("Descrição")
    )

    publico = models.CharField(
        max_length=50,
        verbose_name=_("Público Alvo"),
        null=True,
        blank=True
    )

    pre_requisitos = models.TextField(
        verbose_name=_("Pré-requisitos do Público Alvo"),
        null=True,
        blank=True
    )

    objetivos = models.TextField(
        verbose_name=_("Objetivos"),
        null=True,
        blank=True
    )

    conteudo = models.TextField(
        verbose_name=_("Conteúdo Programático"),
        null=True,
        blank=True
    )

    materiais = models.TextField(
        verbose_name=_("Materiais Necessários"),
        null=True,
        blank=True
    )

    metodologia = models.TextField(
        verbose_name=_("Metodologia"),
        null=True,
        blank=True
    )

    referencias = models.TextField(
        verbose_name=_("Referências Bibliográficas"),
        null=True,
        blank=True
    ) 

    duracao = models.DurationField(
        verbose_name=_("Duração")
    )
    
    com_inscricoes = models.BooleanField(
        default=False,
        verbose_name=_("Permitir inscrições?")
    )

    qtd_vagas = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Quantidade de Vagas")
    )

    inicio_inscricoes = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Iní. das Inscrições")
    )

    fim_inscricoes = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Fim das Inscrições")
    )


    status = models.CharField(
        max_length=30,
        choices=StatusAtividade.choices,
        null=True,
        blank=True,
        verbose_name=_("Status"),
        default=StatusAtividade.RASCUNHO

    )

    
    class Meta:
      verbose_name = 'Atividade'
      verbose_name_plural = 'Atividades'

    @property
    def data_inicio(self):
        agendamento = self._get_primeiro_agendamento()
        return agendamento.dia if agendamento else None

    @property
    def local(self):
        agendamento = self._get_primeiro_agendamento()
        return agendamento.sala if agendamento else None

    def _get_primeiro_agendamento(self):
        return self.agendamentos.filter(dia__gte=self.tipo.evento.dt_inicio).order_by('dia').first()
     
    def __str__(self):
        return f'{self.tipo} - {self.titulo}'
    
    
    def save(self, *args, **kwargs):
        if self.pk and self.status != StatusAtividade.RASCUNHO and self.com_inscricoes:
            total_inscritos = InscricaoAtividade.objects.filter(atividade=self).count()
            if self.qtd_vagas and self.qtd_vagas <= total_inscritos:
                self.status = StatusAtividade.SEM_VAGA
            elif self.inicio_inscricoes <= get_hoje() <= self.fim_inscricoes:
                self.status = StatusAtividade.INSCRICOES_ABERTAS
            elif get_hoje() < self.inicio_inscricoes:
                self.status = StatusAtividade.INSCRICOES_EMBREVE
            else:
                self.status = StatusAtividade.INSCRICOES_ENCERRADAS    

        super().save(*args, **kwargs)

class InscricaoAtividade(models.Model):
    atividade = models.ForeignKey(
        Atividade,
        related_name='inscricoes',
        on_delete=models.CASCADE,
        verbose_name="Atividade"
    )
    usuario = models.ForeignKey(
        User,
        related_name='inscricoes_atividades',
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )
    presente = models.BooleanField(
        default=False,
        verbose_name="Presente"
    )
    data_inscricao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Inscrição"
    )

    def __str__(self):
        return f"{self.usuario} - {self.atividade} (Presente: {self.presente})"
    
    class Meta:
        verbose_name = "Inscrição em Atividade"
        verbose_name_plural = "Inscrições em Atividades"
        unique_together = ('atividade', 'usuario')


class Sala(models.Model):
    nome = models.CharField(
        max_length=100,
        verbose_name=_("Nome da Sala")
    )
    capacidade = models.PositiveIntegerField(
        verbose_name=_("Capacidade"),
        null=True,
        blank=True
    )
    evento = models.ForeignKey(
        Evento,
        related_name='salas',
        on_delete=models.CASCADE,
        verbose_name=_("Evento")
    )

    def __str__(self):
        return f"{self.nome} - {self.evento.titulo}"

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        
class Agendamento(models.Model):
    sala = models.ForeignKey(
        Sala,
        related_name='agendamentos',
        on_delete=models.CASCADE,
        verbose_name=_("Sala")
    )
    atividade = models.ForeignKey(
        Atividade,
        related_name='agendamentos',
        on_delete=models.CASCADE,
        verbose_name=_("Atividade")
    )
    dia = models.DateField(
        verbose_name=_("Dia"),
        default=timezone.now
    )
    inicio = models.TimeField(
        verbose_name=_("Hr Início"),
        default=time(8, 0)
    )
    
    fim = models.TimeField(
        verbose_name=_("Hr Fim"),
        default=time(8, 0)
    )
    

    def __str__(self):
        return f"{self.atividade.titulo} na sala {self.sala.nome} (de {self.inicio.strftime('%H:%M')} até {self.fim.strftime('%H:%M')})"
    @property
    def horario(self):
        return f"{self.inicio.strftime('%H:%M')} até {self.fim.strftime('%H:%M')}"
    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        unique_together = ('sala', 'atividade','dia', 'inicio', 'fim')


class PapelResponsavel(models.TextChoices):
    AUTOR_PRINCIPAL = 'autor_principal', _('Autor Principal')
    COAUTOR = 'coautor', _('Coautor')
    VOLUNTARIO = 'voluntário', _('Voluntário')

class Responsavel(models.Model):
    atividade = models.ForeignKey(
        Atividade,
        related_name='responsaveis',
        on_delete=models.CASCADE,
        verbose_name=_("Atividade")
    )
    
    usuario = models.ForeignKey(
        User,
        related_name='responsavel_atividades',
        on_delete=models.CASCADE,
        verbose_name=_("Usuário")
    )

    papel = models.CharField(
        max_length=30,
        verbose_name=_("Papel"),
        null=False,
        blank=False,
        choices= PapelResponsavel.choices
    )

    def __str__(self):
        return f"{self.usuario} - {self.atividade}"

    class Meta:
        verbose_name = 'Responsável pela Atividade'
        verbose_name_plural = 'Responsáveis pelas Atividades'
        unique_together = ('atividade', 'usuario')

@receiver(post_save, sender=InscricaoAtividade)
def atualizar_status_atividades_on_save_inscricao(
    sender, instance: InscricaoAtividade, created, raw: bool = False, *args, **kwargs
):
    atividade = instance.atividade
    total_inscritos = atividade.inscricoes.count() 

    if total_inscritos >= atividade.qtd_vagas:
        atividade.status = StatusAtividade.SEM_VAGA
        atividade.save()


@receiver(post_delete, sender=InscricaoAtividade)
def atualizar_status_atividades_on_delete_inscricao(
    sender, instance: InscricaoAtividade, *args, **kwargs
):
    atividade = instance.atividade
    total_inscritos = atividade.inscricoes.count()

    if atividade.status == StatusAtividade.SEM_VAGA and total_inscritos < atividade.qtd_vagas:
        atividade.status = StatusAtividade.INSCRICOES_ABERTAS
        atividade.save()
