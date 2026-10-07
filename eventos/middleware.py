from django.utils.deprecation import MiddlewareMixin

from atividades.models import InscricaoAtividade
from .models import Avaliador, Evento, Monitor


class EventoSelecionadoMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.evento = Evento.objects.order_by('-ano', '-pk').first()
        user = request.user
        user.is_evaluator = False
        user.is_monitor = False
        user.avaliador = None
        user.monitor = None
        user.atividades = None
        if user.is_authenticated and request.evento is not None:
            evento = request.evento
            user.is_evaluator = evento.avaliadores.filter(usuario=user).exists()
            user.is_monitor = evento.monitores.filter(usuario=user).exists()
            user.avaliador = Avaliador.objects.filter(usuario=user, evento=evento).first()
            user.monitor = Monitor.objects.filter(usuario=user, evento=evento).first()
            user.atividades = InscricaoAtividade.objects.filter(
                usuario=user, atividade__tipo__evento=evento
            ).first()
