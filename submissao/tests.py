from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from chamadas.models import Chamada, EtapaChamada, StatusChamada, TipoChamada
from documentos.models import Documento
from eventos.models import AreaTematica, Evento
from submissao.forms import MeuTrabalhoAutoSubmissaoForm
from submissao.models import StatusTrabalho, Trabalho
from usuarios.models import User
from usuarios.tables import MeusTrabalhosTable


class TrabalhoSubmissionFlowTests(TestCase):
    def setUp(self):
        self.evento = Evento.objects.create(
            titulo="Evento Teste",
            edicao="2026",
            dt_inicio=date(2026, 1, 10),
            dt_encerramento=date(2026, 1, 20),
            ch_total=10,
            ch_min_certificado=1,
        )
        self.usuario = User.objects.create_user(
            email="participante@example.com",
            password="senha123",
            username="participante",
            nome_completo="Participante Teste",
        )
        self.area = AreaTematica.objects.create(
            evento=self.evento,
            nome="Tecnologia",
        )
        self.tipo_chamada = TipoChamada.objects.create(
            evento=self.evento,
            nome="Chamada de Teste",
            max_autores=3,
            opcoes=["RESUMO", "DESCRICAO"],
        )
        self.chamada = Chamada.objects.create(
            tipo=self.tipo_chamada,
            dt_inicio=date(2026, 1, 1),
            dt_encerramento=date(2026, 1, 30),
            etapa=EtapaChamada.INICIAL,
            status=StatusChamada.ABERTO,
            tem_submissao=True,
        )

    def test_submissoes_p_etapa_does_not_crash_when_missing_submission(self):
        trabalho = Trabalho.objects.create(
            area_tematica=self.area,
            titulo="Trabalho de teste",
            tipo_chamada=self.tipo_chamada,
            autor_principal=self.usuario,
            status=StatusTrabalho.RASCUNHO,
            resumo="Resumo do trabalho",
            palavras_chave="python, django",
            descricao="Descrição do trabalho",
        )

        submissoes = trabalho.submissoes_p_etapa

        self.assertEqual(len(submissoes), 1)
        self.assertEqual(submissoes[0].trabalho, trabalho)
        self.assertEqual(submissoes[0].chamada, self.chamada)
        self.assertIsNone(submissoes[0].documento)

    def test_trabalho_cannot_submit_when_required_data_is_missing(self):
        trabalho = Trabalho.objects.create(
            area_tematica=self.area,
            titulo="Trabalho incompleto",
            tipo_chamada=self.tipo_chamada,
            autor_principal=self.usuario,
            status=StatusTrabalho.RASCUNHO,
        )

        self.assertFalse(trabalho.can_submit())
        self.assertIn("resumo", trabalho.get_missing_submit_fields())
        self.assertIn("palavras_chave", trabalho.get_missing_submit_fields())
        self.assertIn("descricao", trabalho.get_missing_submit_fields())

    def test_submit_checklist_reports_missing_requirements(self):
        trabalho = Trabalho.objects.create(
            area_tematica=self.area,
            titulo="Trabalho incompleto",
            tipo_chamada=self.tipo_chamada,
            autor_principal=self.usuario,
            status=StatusTrabalho.RASCUNHO,
        )

        checklist = trabalho.get_submit_checklist()
        self.assertTrue(any(item["field"] == "resumo" and not item["complete"] for item in checklist))
        self.assertTrue(any(item["field"] == "descricao" and not item["complete"] for item in checklist))

    def test_form_replaces_document_for_same_submission_stage(self):
        trabalho = Trabalho.objects.create(
            area_tematica=self.area,
            titulo="Trabalho com documento",
            tipo_chamada=self.tipo_chamada,
            autor_principal=self.usuario,
            status=StatusTrabalho.RASCUNHO,
            resumo="Resumo do trabalho",
            palavras_chave="python, django",
            descricao="Descrição do trabalho",
        )
        submissao = trabalho.submissoes.create(chamada=self.chamada)

        form = MeuTrabalhoAutoSubmissaoForm()
        form.cleaned_data = {"documento_n_identificado": SimpleUploadedFile("arquivo.pdf", b"conteudo", content_type="application/pdf")}

        form.create_or_update_submission(trabalho, self.chamada)
        submissao.refresh_from_db()
        first_document = submissao.documento

        form.cleaned_data = {"documento_n_identificado": SimpleUploadedFile("arquivo2.pdf", b"conteudo2", content_type="application/pdf")}
        form.create_or_update_submission(trabalho, self.chamada)

        submissao.refresh_from_db()
        self.assertIsNotNone(submissao.documento)
        self.assertEqual(submissao.documento.pk, first_document.pk)
        self.assertEqual(Documento.objects.filter(submissoes=submissao).count(), 1)

    def test_meus_trabalhos_table_handles_missing_open_chamada(self):
        trabalho = Trabalho.objects.create(
            area_tematica=self.area,
            titulo="Trabalho sem chamada aberta",
            tipo_chamada=self.tipo_chamada,
            autor_principal=self.usuario,
            status=StatusTrabalho.SUBMETIDO,
            resumo="Resumo do trabalho",
            palavras_chave="python, django",
            descricao="Descrição do trabalho",
        )

        table = MeusTrabalhosTable(data=[trabalho])
        rendered = table.render_status(trabalho)
        self.assertIn("Submetido", str(rendered))
