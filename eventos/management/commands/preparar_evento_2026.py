from datetime import date

from django.core.management.base import BaseCommand, CommandError

from eventos.models import Evento


class Command(BaseCommand):
    help = 'Cadastra os dados confirmados da Expotec 2026 no banco local.'

    def add_arguments(self, parser):
        parser.add_argument('--edicao', required=True, help='Edição oficial, por exemplo 5ª.')
        parser.add_argument('--ch-total', required=True, type=int, help='Carga horária total confirmada.')

    def handle(self, *args, **options):
        edicao = options['edicao'].strip()
        ch_total = options['ch_total']
        if not edicao:
            raise CommandError('Informe a edição oficial.')
        if ch_total <= 0:
            raise CommandError('A carga horária total deve ser positiva.')

        evento = Evento.objects.filter(ano='2026').first()
        if evento is not None:
            self.stdout.write(f'Evento de 2026 já cadastrado (ID {evento.pk}). Nenhum dado foi alterado.')
            return

        evento = Evento.objects.create(
            titulo='Expotec',
            edicao=edicao,
            ano='2026',
            dt_inicio=date(2026, 11, 23),
            dt_encerramento=date(2026, 11, 27),
            ch_total=ch_total,
        )
        self.stdout.write(self.style.SUCCESS(f'Expotec 2026 criada (ID {evento.pk}).'))
