from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase

from atividades.models import (
    Atividade,
    InscricaoAtividade,
    StatusAtividade,
    TipoAtividade,
)
from eventos.models import Evento
from usuarios.models import User


class StatusAtualAtividadeTests(TestCase):
    def setUp(self):
        self.evento = Evento.objects.create(
            titulo="Expotec",
            edicao="XI",
            ano="2026",
            dt_inicio=date(2026, 11, 23),
            dt_encerramento=date(2026, 11, 27),
            ch_total=20,
        )

        self.tipo = TipoAtividade.objects.create(
            evento=self.evento,
            nome="Oficina",
            cor="#176B75",
        )

        self.atividade = Atividade.objects.create(
            tipo=self.tipo,
            titulo="Workshop de Desenvolvimento Web",
            descricao="Atividade para teste",
            duracao=timedelta(hours=2),
            com_inscricoes=True,
            qtd_vagas=2,
            inicio_inscricoes=date(2026, 11, 1),
            fim_inscricoes=date(2026, 11, 20),
            status=StatusAtividade.INSCRICOES_EMBREVE,
        )

    @patch("atividades.models.get_hoje")
    def test_status_antes_da_abertura(self, mock_hoje):
        mock_hoje.return_value = date(2026, 10, 31)

        self.assertEqual(
            self.atividade.status_atual,
            StatusAtividade.INSCRICOES_EMBREVE,
        )

    @patch("atividades.models.get_hoje")
    def test_status_durante_periodo_de_inscricao(self, mock_hoje):
        mock_hoje.return_value = date(2026, 11, 10)

        self.assertEqual(
            self.atividade.status_atual,
            StatusAtividade.INSCRICOES_ABERTAS,
        )

    @patch("atividades.models.get_hoje")
    def test_status_apos_encerramento(self, mock_hoje):
        mock_hoje.return_value = date(2026, 11, 21)

        self.assertEqual(
            self.atividade.status_atual,
            StatusAtividade.INSCRICOES_ENCERRADAS,
        )

    @patch("atividades.models.get_hoje")
    def test_status_sem_vagas_quando_limite_e_atingido(self, mock_hoje):
        mock_hoje.return_value = date(2026, 11, 10)

        usuario1 = User.objects.create_user(
            username="participante1",
            email="participante1@example.com",
            password="test-password",
        )
        usuario2 = User.objects.create_user(
            username="participante2",
            email="participante2@example.com",
            password="test-password",
        )

        InscricaoAtividade.objects.create(
            atividade=self.atividade,
            usuario=usuario1,
        )
        InscricaoAtividade.objects.create(
            atividade=self.atividade,
            usuario=usuario2,
        )

        self.assertEqual(
            self.atividade.status_atual,
            StatusAtividade.SEM_VAGA,
        )
