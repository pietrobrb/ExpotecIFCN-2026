import rules
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from usuarios.models import Vinculos
@rules.predicate
def is_admin(request):
    if isinstance(request.user, AnonymousUser):
        return False
    evento = getattr(request, 'evento', None)
    if evento is None:
        return False
    return request.user.is_superuser or (request.user.is_authenticated and request.evento.comissoes.all().filter(membros__usuario = request.user, membros__presidente=True).exists())

@rules.predicate
def is_membro(request):
    if isinstance(request.user, AnonymousUser):
        return False
    evento = getattr(request, 'evento', None)
    if evento is None:
        return False
    return request.user.is_superuser or (request.user.is_authenticated and request.evento.comissoes.all().filter(membros__usuario = request.user).exists())

@rules.predicate
def is_participante(request):
    if isinstance(request.user, AnonymousUser):
        return False
   
    evento = getattr(request, 'evento', None)
    if evento is None:
        return False
        
    return request.user.is_authenticated and request.evento.inscricoes.filter(usuario = request.user).exists()

@rules.predicate
def is_evaluator(request):
    if isinstance(request.user, AnonymousUser):
        return False
   
    evento = getattr(request, 'evento', None)
    if evento is None:
        return False
    return request.user.is_authenticated and request.evento.avaliadores.filter(usuario = request.user).exists()

@rules.predicate
def can_evaluate(request):
    if isinstance(request.user, AnonymousUser):
        return False
    return request.user.vinculo == Vinculos.SERVIDOR and not request.user.is_evaluator

@rules.predicate
def can_monitor(request):
    if isinstance(request.user, AnonymousUser):
        return False
    return request.user.vinculo == Vinculos.ALUNO and not request.user.is_monitor

@rules.predicate
def is_monitor(request):
    if isinstance(request.user, AnonymousUser):
        return False
   
    evento = getattr(request, 'evento', None)
    if evento is None:
        return False
    return request.user.is_authenticated and request.evento.monitores.filter(usuario = request.user).exists()

@rules.predicate
def is_user(request):
    return request.user.is_authenticated



rules.add_rule('is_user_rule', is_user)
rules.add_rule('is_participant_rule', is_participante)
rules.add_rule('is_member_rule', is_membro)
rules.add_rule('is_admin_rule', is_admin)
rules.add_rule('can_evaluate_rule', can_evaluate)
rules.add_rule('is_evaluator_rule', is_evaluator)
rules.add_rule('can_monitor_rule', can_monitor)
rules.add_rule('is_monitor_rule', is_monitor)