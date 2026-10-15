import uuid

from django.db import models
from django.utils import timezone

from atividades.models import Agendamento, InscricaoAtividade
from eventos.models import Monitor


class StatusSessaoPresenca(models.TextChoices):
    AGUARDANDO = "aguardando", "Aguardando"
    ABERTA = "aberta", "Presença aberta"
    ENCERRADA = "encerrada", "Presença encerrada"
    INICIADA = "iniciada", "Atividade iniciada"


class SessaoPresenca(models.Model):
    agendamento = models.OneToOneField(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="sessao_presenca",
        verbose_name="Agendamento",
    )

    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessoes_presenca",
        verbose_name="Monitor",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusSessaoPresenca.choices,
        default=StatusSessaoPresenca.AGUARDANDO,
        verbose_name="Status",
    )

    inicio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Início da presença",
    )

    prazo_encerramento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Prazo máximo da chamada",
    )

    fim = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fim da presença",
    )

    token_atual = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name="Token atual",
    )

    token_expira_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expiração do token",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        verbose_name = "Sessão de Presença"
        verbose_name_plural = "Sessões de Presença"
        ordering = ["-criado_em"]

    def __str__(self):
        return (
            f"{self.agendamento.atividade.titulo} - "
            f"{self.agendamento.dia} "
            f"{self.agendamento.inicio.strftime('%H:%M')}"
        )

    @property
    def token_valido(self):
        return (
            self.status == StatusSessaoPresenca.ABERTA
            and self.token_expira_em is not None
            and timezone.now() < self.token_expira_em
        )

    def renovar_token(self, validade_segundos=30):
        self.token_atual = uuid.uuid4()
        self.token_expira_em = timezone.now() + timezone.timedelta(
            seconds=validade_segundos
        )
        self.save(
            update_fields=[
                "token_atual",
                "token_expira_em",
                "atualizado_em",
            ]
        )

    def abrir(self, validade_segundos=30):
        agora = timezone.now()

        self.status = StatusSessaoPresenca.ABERTA
        self.inicio = agora
        self.fim = None
        self.prazo_encerramento = agora + timezone.timedelta(minutes=10)
        self.token_atual = uuid.uuid4()
        self.token_expira_em = agora + timezone.timedelta(seconds=validade_segundos)

        self.save(
            update_fields=[
                "monitor",
                "status",
                "inicio",
                "fim",
                "prazo_encerramento",
                "token_atual",
                "token_expira_em",
                "atualizado_em",
            ]
        )

    def encerrar(self):
        if self.status != StatusSessaoPresenca.ABERTA:
            return

        self.status = StatusSessaoPresenca.ENCERRADA
        self.fim = timezone.now()
        self.token_expira_em = None

        self.save(
            update_fields=[
                "status",
                "fim",
                "token_expira_em",
                "atualizado_em",
            ]
        )

    def prazo_esgotado(self):
        return (
            self.prazo_encerramento is not None
            and timezone.now() >= self.prazo_encerramento
        )


    def todos_presentes(self):
        inscricoes = InscricaoAtividade.objects.filter(
            atividade=self.agendamento.atividade
        )

        total_inscritos = inscricoes.count()

        total_presentes = (
            self.registros
            .filter(inscricao__atividade=self.agendamento.atividade)
            .values("inscricao_id")
            .distinct()
            .count()
        )

        return (
            total_inscritos > 0
            and total_presentes >= total_inscritos
        )


    def iniciar_atividade(self):
        if self.status != StatusSessaoPresenca.ENCERRADA:
            return False

        self.status = StatusSessaoPresenca.INICIADA
        self.save(update_fields=["status", "atualizado_em"])
        return True


class RegistroPresenca(models.Model):
    sessao = models.ForeignKey(
        SessaoPresenca,
        on_delete=models.CASCADE,
        related_name="registros",
        verbose_name="Sessão de presença",
    )

    inscricao = models.ForeignKey(
        InscricaoAtividade,
        on_delete=models.CASCADE,
        related_name="registros_presenca",
        verbose_name="Inscrição",
    )

    registrado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Registrado em",
    )

    class Meta:
        verbose_name = "Registro de Presença"
        verbose_name_plural = "Registros de Presença"
        constraints = [
            models.UniqueConstraint(
                fields=["sessao", "inscricao"],
                name="unique_presenca_sessao_inscricao",
            )
        ]
        ordering = ["registrado_em"]

    def __str__(self):
        return (
            f"{self.inscricao.usuario} - " f"{self.sessao.agendamento.atividade.titulo}"
        )
