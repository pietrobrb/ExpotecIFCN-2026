from datetime import date, time, timedelta

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from atividades.models import (
    Agendamento,
    Atividade,
    InscricaoAtividade,
    Sala,
    TipoAtividade,
)
from eventos.models import Evento, Monitor
from usuarios.models import User

from .models import (
    RegistroPresenca,
    SessaoPresenca,
    StatusSessaoPresenca,
)


class ControlePresencaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.evento = Evento.objects.create(
            titulo="Expotec Teste",
            edicao="XI",
            ano="2026",
            dt_inicio=date(2026, 11, 23),
            dt_encerramento=date(2026, 11, 27),
            ch_total=40,
        )

        cls.monitor_usuario = User.objects.create_user(
            email="monitor@example.com",
            username="monitor",
            nome_completo="Monitor Teste",
            password="SenhaTeste123!",
        )

        cls.aluno = User.objects.create_user(
            email="aluno@example.com",
            username="aluno",
            nome_completo="Aluno Teste",
            password="SenhaTeste123!",
        )

        cls.nao_inscrito = User.objects.create_user(
            email="externo@example.com",
            username="externo",
            nome_completo="Usuario Externo",
            password="SenhaTeste123!",
        )

        cls.monitor = Monitor.objects.create(
            usuario=cls.monitor_usuario,
            evento=cls.evento,
        )

        cls.tipo = TipoAtividade.objects.create(
            evento=cls.evento,
            nome="Workshop",
            descricao="Atividade para testes",
            cor="#000000",
            icone="book",
        )

        cls.atividade = Atividade.objects.create(
            tipo=cls.tipo,
            titulo="Workshop de Teste",
            descricao="Atividade de teste",
            duracao=timedelta(hours=2),
        )

        cls.sala = Sala.objects.create(
            nome="Laboratório de Teste",
            capacidade=30,
            evento=cls.evento,
        )

        cls.agendamento = Agendamento.objects.create(
            sala=cls.sala,
            atividade=cls.atividade,
            dia=date(2026, 11, 23),
            inicio=time(14, 0),
            fim=time(16, 0),
        )

        cls.inscricao = InscricaoAtividade.objects.create(
            atividade=cls.atividade,
            usuario=cls.aluno,
        )

    def test_abrir_presenca_associa_monitor_a_sessao(self):
        self.client.force_login(self.monitor_usuario)

        resposta = self.client.post(
            reverse(
                "presenca:abrir_presenca",
                kwargs={"agendamento_id": self.agendamento.pk},
            )
        )

        self.assertRedirects(
            resposta,
            reverse("presenca:monitor"),
        )

        sessao = SessaoPresenca.objects.get(
            agendamento=self.agendamento,
        )
        self.assertEqual(sessao.monitor, self.monitor)
        self.assertEqual(sessao.status, StatusSessaoPresenca.ABERTA)
        self.assertIsNotNone(sessao.token_atual)

    def test_painel_nao_oferece_controle_para_sessao_sem_monitor(self):
        sessao = SessaoPresenca.objects.create(
            agendamento=self.agendamento,
            monitor=None,
            status=StatusSessaoPresenca.INICIADA,
        )

        self.client.force_login(self.monitor_usuario)

        resposta = self.client.get(reverse("presenca:monitor"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(
            resposta,
            "Esta sessão não possui monitor associado e não pode ser controlada.",
        )
        self.assertNotContains(
            resposta,
            reverse(
                "presenca:controle_sessao",
                kwargs={"sessao_id": sessao.pk},
            ),
        )

    def criar_sessao_aberta(self):
        sessao = SessaoPresenca.objects.create(
            agendamento=self.agendamento,
            monitor=self.monitor,
        )
        sessao.abrir(validade_segundos=30)
        return sessao

    def test_abertura_define_prazo_de_dez_minutos(self):
        antes = timezone.now()
        sessao = self.criar_sessao_aberta()
        depois = timezone.now()

        self.assertEqual(sessao.status, StatusSessaoPresenca.ABERTA)
        self.assertGreaterEqual(
            sessao.prazo_encerramento,
            antes + timedelta(minutes=10),
        )
        self.assertLessEqual(
            sessao.prazo_encerramento,
            depois + timedelta(minutes=10),
        )
        self.assertLessEqual(
            sessao.token_expira_em - sessao.inicio,
            timedelta(seconds=30),
        )

    def test_checkin_valido_registra_presenca(self):
        sessao = self.criar_sessao_aberta()
        self.client.force_login(self.aluno)

        resposta = self.client.get(
            reverse(
                "presenca:checkin",
                kwargs={"token": sessao.token_atual},
            )
        )

        self.assertEqual(resposta.status_code, 200)

        self.inscricao.refresh_from_db()
        self.assertTrue(self.inscricao.presente)
        self.assertEqual(
            RegistroPresenca.objects.filter(
                sessao=sessao,
                inscricao=self.inscricao,
            ).count(),
            1,
        )

    def test_usuario_nao_inscrito_nao_registra_presenca(self):
        sessao = self.criar_sessao_aberta()
        self.client.force_login(self.nao_inscrito)

        resposta = self.client.get(
            reverse(
                "presenca:checkin",
                kwargs={"token": sessao.token_atual},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(RegistroPresenca.objects.filter(sessao=sessao).exists())

    def test_sessao_encerrada_bloqueia_checkin(self):
        sessao = self.criar_sessao_aberta()
        sessao.encerrar()
        self.client.force_login(self.aluno)

        resposta = self.client.get(
            reverse(
                "presenca:checkin",
                kwargs={"token": sessao.token_atual},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(RegistroPresenca.objects.filter(sessao=sessao).exists())

    def test_atividade_nao_inicia_com_chamada_aberta(self):
        sessao = self.criar_sessao_aberta()

        resultado = sessao.iniciar_atividade()

        sessao.refresh_from_db()
        self.assertFalse(resultado)
        self.assertEqual(sessao.status, StatusSessaoPresenca.ABERTA)

    def test_atividade_inicia_apos_encerramento(self):
        sessao = self.criar_sessao_aberta()
        sessao.encerrar()

        resultado = sessao.iniciar_atividade()

        sessao.refresh_from_db()
        self.assertTrue(resultado)
        self.assertEqual(sessao.status, StatusSessaoPresenca.INICIADA)

    def test_chamada_expirada_e_encerrada_ao_renovar_qr(self):
        sessao = self.criar_sessao_aberta()
        sessao.prazo_encerramento = timezone.now() - timedelta(seconds=1)
        sessao.save(update_fields=["prazo_encerramento"])

        self.client.force_login(self.monitor_usuario)

        resposta = self.client.post(
            reverse(
                "presenca:renovar_presenca",
                kwargs={"sessao_id": sessao.id},
            )
        )

        sessao.refresh_from_db()

        self.assertEqual(sessao.status, StatusSessaoPresenca.ENCERRADA)
        self.assertEqual(resposta.status_code, 400)

    def test_token_expirado_nao_registra_presenca(self):
        sessao = self.criar_sessao_aberta()
        sessao.token_expira_em = timezone.now() - timedelta(seconds=1)
        sessao.save(update_fields=["token_expira_em"])

        self.client.force_login(self.aluno)

        resposta = self.client.get(
            reverse(
                "presenca:checkin",
                kwargs={"token": sessao.token_atual},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(RegistroPresenca.objects.filter(sessao=sessao).exists())

    def test_presenca_anterior_nao_conta_na_sessao_atual(self):
        sessao = self.criar_sessao_aberta()

        # Simula uma presença marcada anteriormente na inscrição.
        self.inscricao.presente = True
        self.inscricao.save(update_fields=["presente"])

        # A inscrição ainda não possui registro nesta sessão.
        self.assertFalse(sessao.todos_presentes())

    def test_todos_presentes_considera_registros_da_sessao(self):
        sessao = self.criar_sessao_aberta()

        RegistroPresenca.objects.create(
            sessao=sessao,
            inscricao=self.inscricao,
        )

        self.assertTrue(sessao.todos_presentes())

    def test_renovacao_qr_usa_base_url_configurada(self):
        from django.conf import settings

        sessao = self.criar_sessao_aberta()
        self.client.force_login(self.monitor_usuario)

        resposta = self.client.post(
            reverse(
                "presenca:renovar_presenca",
                kwargs={"sessao_id": sessao.id},
            )
        )

        self.assertEqual(resposta.status_code, 200)

        dados = resposta.json()

        self.assertTrue(
            dados["checkin_url"].startswith(f"{settings.BASE_URL}/presenca/checkin/")
        )

    def test_controle_sessao_usa_base_url_configurada(self):
        from django.conf import settings

        sessao = self.criar_sessao_aberta()
        self.client.force_login(self.monitor_usuario)

        resposta = self.client.get(
            reverse(
                "presenca:controle_sessao",
                kwargs={"sessao_id": sessao.id},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.context["checkin_url"],
            f"{settings.BASE_URL}/presenca/checkin/{sessao.token_atual}/",
        )
