from datetime import date

from django.core.management.base import BaseCommand, CommandError

from enderecos.models import Cidade, Endereco, Estado
from eventos.models import Evento


class Command(BaseCommand):
    help = (
        'Cadastra a Expotec 2026 no banco local com dados provisorios. '
        'Tudo que ainda nao foi divulgado fica vazio ("Em breve" no portal) '
        'e pode ser editado depois pelo sistema.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--edicao', default='XI', help='Edicao oficial. Padrao: XI.')
        parser.add_argument(
            '--ch-total', type=int, default=1,
            help='Carga horaria total. Valor provisorio (1) ate a divulgacao oficial.',
        )

    def handle(self, *args, **options):
        edicao = options['edicao'].strip()
        ch_total = options['ch_total']
        if not edicao:
            raise CommandError('Informe a edicao oficial.')
        if ch_total <= 0:
            raise CommandError('A carga horaria total deve ser positiva.')

        evento = Evento.objects.filter(ano='2026').first()
        if evento is not None:
            self.stdout.write(f'Evento de 2026 ja cadastrado (ID {evento.pk}). Nenhum dado foi alterado.')
            return

        endereco = self._endereco_campus()
        evento = Evento.objects.create(
            titulo='Expotec',
            edicao=edicao,
            ano='2026',
            dt_inicio=date(2026, 11, 23),
            dt_encerramento=date(2026, 11, 27),
            ch_total=ch_total,
            endereco=endereco,
        )
        self.stdout.write(self.style.SUCCESS(f'Expotec 2026 criada (ID {evento.pk}).'))
        self.stdout.write(
            'Pendentes (editar depois no sistema): carga horaria total, apresentacao, '
            'subtitulo, contatos, salas, tipos de atividade e programacao.'
        )

    def _endereco_campus(self):
        cidade = Cidade.objects.filter(
            nome__iexact='Currais Novos', estado__sigla='RN'
        ).first()
        if cidade is None:
            self.stdout.write(self.style.WARNING(
                'Cidade Currais Novos/RN nao encontrada (rode o loaddata do initial.json). '
                'O evento sera criado sem endereco.'
            ))
            return None
        return Endereco.objects.create(
            estado=Estado.objects.get(pk=cidade.estado_id),
            cidade=cidade,
            logradouro='Em breve',
            local='IFRN - Campus Currais Novos',
        )
