from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase

from atividades.models import Atividade, TipoAtividade
from eventos.forms import EventoForm
from eventos.models import Comissao, Evento, InscricaoEvento, Membro, Noticia
from usuarios.models import User


def criar_evento(**kwargs):
    dados = dict(
        titulo="Expotec",
        edicao="XI",
        ano="2026",
        dt_inicio=date(2026, 11, 23),
        dt_encerramento=date(2026, 11, 27),
        ch_total=20,
    )
    dados.update(kwargs)
    return Evento.objects.create(**dados)


def criar_usuario(nome):
    return User.objects.create_user(
        username=nome,
        email=f"{nome}@example.com",
        password="test-password",
        nome_completo=nome.capitalize(),
    )


class EventoModelTests(TestCase):
    def setUp(self):
        self.evento = criar_evento()

    def test_str_mostra_edicao_e_titulo(self):
        self.assertEqual(str(self.evento), "XI - Expotec")

    def test_dias_do_evento_cobre_do_inicio_ao_encerramento(self):
        dias = self.evento.dias_do_evento
        self.assertEqual(len(dias), 5)
        self.assertEqual(dias[0], date(2026, 11, 23))
        self.assertEqual(dias[-1], date(2026, 11, 27))

    def test_usuarios_inscritos(self):
        usuario = criar_usuario("inscrito")
        InscricaoEvento.objects.create(evento=self.evento, usuario=usuario)
        self.assertEqual(list(self.evento.usuarios_inscritos), [usuario.pk])

    def test_inscricao_duplicada_nao_e_permitida(self):
        usuario = criar_usuario("duplicado")
        InscricaoEvento.objects.create(evento=self.evento, usuario=usuario)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                InscricaoEvento.objects.create(evento=self.evento, usuario=usuario)

    def test_presidentes_e_membros_da_comissao(self):
        comissao = Comissao.objects.create(evento=self.evento, nome="Comissão Geral")
        presidente = criar_usuario("presidente")
        membro = criar_usuario("membro")
        Membro.objects.create(comissao=comissao, usuario=presidente, presidente=True)
        Membro.objects.create(comissao=comissao, usuario=membro, presidente=False)
        self.assertEqual(self.evento.usuarios_presidentes, [presidente])
        self.assertEqual(self.evento.usuarios_membros, [membro])

    def test_atividades_so_traz_as_do_proprio_evento(self):
        outro = criar_evento(ano="2024", edicao="IV",
                             dt_inicio=date(2024, 12, 16),
                             dt_encerramento=date(2024, 12, 19))
        tipo = TipoAtividade.objects.create(evento=self.evento, nome="Oficina", cor="#176B75")
        tipo_outro = TipoAtividade.objects.create(evento=outro, nome="Oficina", cor="#176B75")
        minha = Atividade.objects.create(
            tipo=tipo, titulo="Minha", descricao="x",
            duracao=timedelta(hours=2), qtd_vagas=10,
        )
        Atividade.objects.create(
            tipo=tipo_outro, titulo="De outro evento", descricao="x",
            duracao=timedelta(hours=2), qtd_vagas=10,
        )
        self.assertEqual(list(self.evento.atividades), [minha])


class NoticiaTests(TestCase):
    def setUp(self):
        self.evento = criar_evento()

    def criar(self, titulo, **kwargs):
        return Noticia.objects.create(evento=self.evento, titulo=titulo, texto="texto", **kwargs)

    def test_ordem_automatica_segue_a_quantidade_de_noticias(self):
        primeira = self.criar("Primeira")
        segunda = self.criar("Segunda")
        self.assertEqual(primeira.ordem, 1)
        self.assertEqual(segunda.ordem, 2)

    def test_ordem_repetida_empurra_a_noticia_existente(self):
        antiga = self.criar("Antiga")
        nova = self.criar("Nova", ordem=1)
        antiga.refresh_from_db()
        self.assertEqual(nova.ordem, 1)
        self.assertEqual(antiga.ordem, 2)

    def test_top5_noticias_limita_e_ordena(self):
        for i in range(7):
            self.criar(f"Noticia {i}")
        ordens = [n.ordem for n in self.evento.top5_noticias]
        self.assertEqual(ordens, [1, 2, 3, 4, 5])


class EventoFormTests(TestCase):
    def dados(self, **kwargs):
        dados = {
            "titulo": "Expotec",
            "edicao": "XI",
            "ano": "2026",
            "dt_inicio": "2026-11-23",
            "dt_encerramento": "2026-11-27",
            "ch_total": 20,
        }
        dados.update(kwargs)
        return dados

    def test_datas_validas(self):
        form = EventoForm(data=self.dados())
        self.assertTrue(form.is_valid(), form.errors)

    def test_encerramento_antes_do_inicio_e_invalido(self):
        form = EventoForm(data=self.dados(dt_encerramento="2026-11-22"))
        self.assertFalse(form.is_valid())
        self.assertIn("dt_encerramento", form.errors)
