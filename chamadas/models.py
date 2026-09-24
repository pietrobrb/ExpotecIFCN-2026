from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import get_hoje
from documentos.models import Documento
from eventos.models import Evento
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator

from multiselectfield import MultiSelectField

from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
class OpcoesChamada(models.TextChoices):
    RESUMO = "RESUMO", _("Resumo")
    DESCRICAO = "DESCRICAO", _("Descrição")


class TipoChamada(models.Model):
    evento = models.ForeignKey(
        Evento, 
        related_name='tipos_chamadas', 
        on_delete=models.CASCADE, 
        verbose_name=_("Evento")
    )
    nome = models.CharField(
        max_length=50,
        verbose_name=_("Nome")
    )

    descricao = models.TextField(
        verbose_name=_("Descrição"),
        blank=True,
        null=True
    )

    max_autores = models.PositiveIntegerField(
        verbose_name=_("Máximo de Autores"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9) 
        ],
        null=True, 
        blank=True
    )

    opcoes = MultiSelectField(
        max_length=255,
        choices=OpcoesChamada.choices,
        verbose_name=_("Campos opcionais"),
        default=OpcoesChamada.RESUMO,
        null= True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Tipo de Chamada'
        verbose_name_plural = 'Tipos de Chamadas'

    def __str__(self):
        return self.nome.capitalize()


    @property
    def chamada_atual(self):
        return self.chamadas.filter(
            models.Q(status=StatusChamada.ABERTO) | models.Q(status=StatusChamada.EM_BREVE)
        ).order_by('dt_inicio').first()
    
    @property
    def primeira_chamada(self):
        return self.chamadas.filter(etapa = EtapaChamada.INICIAL).exclude(status=StatusChamada.RASCUNHO).order_by('dt_inicio').first()
    
    @property
    def segunda_chamada(self):
        return self.chamadas.filter(etapa = EtapaChamada.APRESENTACAO).exclude(status=StatusChamada.RASCUNHO).order_by('dt_inicio').first()
    

    @property
    def ultima_chamada(self):
        return self.chamadas.filter(etapa = EtapaChamada.FINAL).exclude(status=StatusChamada.RASCUNHO).order_by('dt_inicio').first()
    
    @property
    def lista_chamadas(self):
        return self.chamadas.all().exclude(status=StatusChamada.RASCUNHO).order_by('dt_inicio')
    
class EtapaChamada(models.TextChoices):
        INICIAL = 'inicial', _("Inicial")
        APRESENTACAO = 'apresentacao', _("Apresentação")
        FINAL = 'final', _("Final")

class StatusChamada(models.TextChoices):
    ABERTO = 'aberto', _("Aberto")
    ENCERRADO = 'encerrado', _("Encerrado")
    EM_BREVE = 'em_breve', _("Em Breve")
    RASCUNHO = 'rascunho', _("Rascunho")

class FormaAvaliacao(models.TextChoices):
    SEM = 'sem', _("Sem Avaliação")
    SOMA = 'soma', _("Soma Simples")
    MEDIA_ARITMETICA = 'media_aritmetica', _("Média Aritmética")
    MEDIA_PONDERADA = 'media_ponderada', _("Média Ponderada")

class Chamada(models.Model):
    tipo = models.ForeignKey(
        TipoChamada,
        related_name='chamadas',
        on_delete=models.CASCADE,
        verbose_name=_("Tipo")
    )
    dt_inicio = models.DateField(
        verbose_name=_("Data de Início"),
         default=datetime.date.today
    )
    dt_encerramento = models.DateField(
        verbose_name=_("Data de Encerramento"),
         default=datetime.date.today
    )
    etapa = models.CharField(
        max_length=20,
        choices=EtapaChamada.choices,
        verbose_name=_("Etapa"),
        default=EtapaChamada.INICIAL
    )
    tem_submissao = models.BooleanField(
        verbose_name=_("Tem Submissão"),
        default=True
    )

    forma_avaliacao = models.CharField(
        max_length=20,
        verbose_name=_("Forma de Avaliação"),
        choices=FormaAvaliacao.choices,
        default=FormaAvaliacao.MEDIA_PONDERADA,
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChamada.choices,
        default=StatusChamada.EM_BREVE,
        verbose_name=_("Status")
    )

    min_aprovacoes = models.PositiveIntegerField(default=1, verbose_name=_("Mínimo de Aprovações"))

    min_avaliacoes = models.PositiveIntegerField(
            verbose_name=_("Mínimo de Avaliações"),
            default=0,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(5) 
            ]
    )
  
    class Meta:
        verbose_name = 'Chamada'
        verbose_name_plural = 'Chamadas'

    def __str__(self):
        return f"{self.tipo} - {self.get_etapa_display()} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if self.status != StatusChamada.RASCUNHO:
            if self.dt_inicio <= get_hoje() <= self.dt_encerramento:
                  self.status = StatusChamada.ABERTO
            elif get_hoje() < self.dt_inicio:
                self.status = StatusChamada.EM_BREVE
            elif get_hoje() > self.dt_encerramento:
                self.status = StatusChamada.ENCERRADO
        super().save(*args, **kwargs)

class CriterioAvaliacao(models.Model):
    chamada = models.ForeignKey(
        Chamada,
        related_name='criterios_avaliacao',
        on_delete=models.CASCADE,
        verbose_name=_("Chamada")
    )
    nome = models.CharField(max_length=30, verbose_name=_("Nome"))
    descricao = models.CharField(max_length=255,blank=True, null=True, verbose_name=_("Descrição"))
    peso = models.PositiveIntegerField(verbose_name=_("Peso"))

    def __str__(self):
        return f"{self.nome}: {self.descricao}" if self.descricao else self.nome

    class Meta:
        verbose_name = _("Critério de Avaliação")
        verbose_name_plural = _("Critérios de Avaliação")

class TipoChamadaDocumento(models.Model):
    tipo_chamada = models.ForeignKey(
        TipoChamada,
        on_delete=models.CASCADE,
        related_name='tipo_chamada_documentos',
        verbose_name=_("Documento")
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='tipo_chamada_documentos',
        verbose_name=_("Documento")
    )

    class Meta:
        unique_together = ('tipo_chamada', 'documento') 
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
    
    def __str__(self) -> str:
        return f'{self.tipo_chamada.nome} - {self.documento}'
    


@receiver(post_save, sender=Chamada)
def atualizar_status_trabalho_on_save_chamada(
    sender, instance: Chamada, created, raw: bool = False, *args, **kwargs
):
    if not created:
        for s in instance.submissoes.all():
            s.processar_avaliacao()