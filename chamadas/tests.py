import datetime

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from chamadas.models import Chamada, FormaAvaliacao


def nova_chamada(**kwargs):
    """Chamada em memória (sem banco) para testar Chamada.clean()."""
    dados = dict(
        dt_inicio=datetime.date(2026, 9, 1),
        dt_encerramento=datetime.date(2026, 9, 30),
        forma_avaliacao=FormaAvaliacao.MEDIA_PONDERADA,
        min_avaliacoes=2,
        min_aprovacoes=1,
    )
    dados.update(kwargs)
    return Chamada(**dados)


class ChamadaCleanTests(SimpleTestCase):
    def test_chamada_valida(self):
        nova_chamada().clean()

    def test_data_de_encerramento_antes_do_inicio(self):
        chamada = nova_chamada(dt_encerramento=datetime.date(2026, 8, 1))
        with self.assertRaises(ValidationError) as ctx:
            chamada.clean()
        self.assertIn('dt_encerramento', ctx.exception.message_dict)

    def test_inicio_e_encerramento_no_mesmo_dia_e_valido(self):
        dia = datetime.date(2026, 9, 10)
        nova_chamada(dt_inicio=dia, dt_encerramento=dia).clean()

    def test_com_avaliacao_exige_min_avaliacoes(self):
        chamada = nova_chamada(min_avaliacoes=0)
        with self.assertRaises(ValidationError) as ctx:
            chamada.clean()
        self.assertIn('min_avaliacoes', ctx.exception.message_dict)

    def test_sem_avaliacao_aceita_min_avaliacoes_zero(self):
        nova_chamada(forma_avaliacao=FormaAvaliacao.SEM, min_avaliacoes=0).clean()

    def test_min_aprovacoes_nao_pode_superar_min_avaliacoes(self):
        chamada = nova_chamada(min_avaliacoes=2, min_aprovacoes=3)
        with self.assertRaises(ValidationError) as ctx:
            chamada.clean()
        self.assertIn('min_aprovacoes', ctx.exception.message_dict)
