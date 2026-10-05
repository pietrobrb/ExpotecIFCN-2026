from datetime import date, timedelta
from io import BytesIO
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from usuarios.views import CertificadoAtividadePdfView, CertificadoEventoPdfView
from PIL import Image

from atividades.models import Atividade, InscricaoAtividade, TipoAtividade
from enderecos.models import Contato
from eventos.models import Evento
from usuarios.certificados import generate_certificate_pdf, get_user_certificate_data
from usuarios.models import User


class CertificateTests(TestCase):
	def setUp(self):
		self.media_dir = tempfile.TemporaryDirectory()
		self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
		self.settings_override.enable()
		self.addCleanup(self.settings_override.disable)
		self.addCleanup(self.media_dir.cleanup)

		self.event = Evento.objects.create(
			titulo="Expotec",
			edicao="XI",
			ano="2026",
			dt_inicio=date(2026, 11, 23),
			dt_encerramento=date(2026, 11, 27),
			ch_total=20,
			ch_min_certificado=3,
		)
		self.user = User.objects.create_user(
			username="participante",
			email="participante@example.com",
			password="test-password",
			nome_completo="Pessoa Participante",
		)
		self.activity_type = TipoAtividade.objects.create(
			evento=self.event,
			nome="Oficina",
			cor="#176B75",
		)
		self.activity = Atividade.objects.create(
			tipo=self.activity_type,
			titulo="Introdução à Robótica",
			descricao="Atividade de teste",
			duracao=timedelta(hours=2),
			qtd_vagas=10,
		)

	def configure_signatory(self):
		signature_image = BytesIO()
		Image.new("RGBA", (120, 40), (0, 0, 0, 0)).save(signature_image, format="PNG")
		self.event.certificado_signatario_nome = "Responsável do Evento"
		self.event.certificado_signatario_cargo = "Coordenação Geral"
		self.event.certificado_signatario_assinatura = SimpleUploadedFile(
			"assinatura.png",
			signature_image.getvalue(),
			content_type="image/png",
		)
		self.event.save()

	def test_only_confirmed_presence_counts_toward_event_certificate(self):
		confirmed = InscricaoAtividade.objects.create(
			atividade=self.activity,
			usuario=self.user,
			presente=True,
		)
		another_activity = Atividade.objects.create(
			tipo=self.activity_type,
			titulo="Atividade sem presença",
			descricao="Atividade de teste",
			duracao=timedelta(hours=2),
			qtd_vagas=10,
		)
		unconfirmed = InscricaoAtividade.objects.create(
			atividade=another_activity,
			usuario=self.user,
			presente=False,
		)

		summary = get_user_certificate_data(self.user, self.event)
		self.assertEqual(summary["activity_certificates"], [confirmed])
		self.assertEqual(summary["total_duration"], timedelta(hours=2))
		self.assertFalse(summary["event_eligible"])

		unconfirmed.presente = True
		unconfirmed.save(update_fields=["presente"])
		summary = get_user_certificate_data(self.user, self.event)
		self.assertEqual(summary["total_duration"], timedelta(hours=4))
		self.assertTrue(summary["event_eligible"])

	def test_pdf_is_generated_with_event_signatory(self):
		self.configure_signatory()

		pdf = generate_certificate_pdf(
			self.event,
			self.user,
			self.activity.duracao,
			activity=self.activity,
		)

		self.assertTrue(pdf.startswith(b"%PDF"))

	def test_activity_download_is_limited_to_confirmed_participant(self):
		self.configure_signatory()
		InscricaoAtividade.objects.create(
			atividade=self.activity,
			usuario=self.user,
			presente=True,
		)
		request = RequestFactory().get("/users/me/certificados/")
		request.user = self.user
		request.evento = self.event
		response = CertificadoAtividadePdfView.as_view()(
			request,
			atividade_id=self.activity.pk,
		)
		self.assertEqual(response["Content-Type"], "application/pdf")
		self.assertTrue(response.content.startswith(b"%PDF"))

		other_user = User.objects.create_user(
			username="outra-pessoa",
			email="outra@example.com",
			password="test-password",
			nome_completo="Outra Pessoa",
		)
		request = RequestFactory().get("/users/me/certificados/")
		request.user = other_user
		request.evento = self.event
		with self.assertRaises(Http404):
			CertificadoAtividadePdfView.as_view()(
				request,
				atividade_id=self.activity.pk,
			)

	def test_event_download_requires_minimum_confirmed_hours(self):
		self.configure_signatory()
		InscricaoAtividade.objects.create(
			atividade=self.activity,
			usuario=self.user,
			presente=True,
		)
		request = RequestFactory().get("/users/me/certificados/evento.pdf")
		request.user = self.user
		request.evento = self.event
		with self.assertRaises(Http404):
			CertificadoEventoPdfView.as_view()(request)

		another_activity = Atividade.objects.create(
			tipo=self.activity_type,
			titulo="Outra atividade",
			descricao="Atividade de teste",
			duracao=timedelta(hours=1),
			qtd_vagas=10,
		)
		InscricaoAtividade.objects.create(
			atividade=another_activity,
			usuario=self.user,
			presente=True,
		)
		response = CertificadoEventoPdfView.as_view()(request)
		self.assertEqual(response["Content-Type"], "application/pdf")
		self.assertTrue(response.content.startswith(b"%PDF"))


class SupportPageTests(TestCase):
	def setUp(self):
		self.event = Evento.objects.create(
			titulo="Expotec",
			edicao="XI",
			ano="2026",
			dt_inicio=date(2026, 11, 23),
			dt_encerramento=date(2026, 11, 27),
			ch_total=20,
		)
		self.user = User.objects.create_user(
			username="participante",
			email="participante@example.com",
			password="test-password",
			nome_completo="Pessoa Participante",
		)
		self.client.force_login(self.user)

	def test_support_page_shows_message_when_event_has_no_contacts(self):
		response = self.client.get(reverse("user:suporte"), HTTP_HOST="127.0.0.1")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Como podemos ajudar?")
		self.assertContains(response, "A organização ainda não publicou contatos")

	def test_support_page_shows_event_contact_links(self):
		contact = Contato.objects.create(
			nome="Organização",
			email="organizacao@example.com",
			telefone="84999990000",
		)
		self.event.contatos.add(contact)

		response = self.client.get(reverse("user:suporte"), HTTP_HOST="127.0.0.1")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "mailto:organizacao@example.com")
		self.assertContains(response, "tel:84999990000")
