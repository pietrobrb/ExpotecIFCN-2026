from django.urls import reverse
import rules
from simple_menu import Menu, MenuItem

# Menu principal
main = "main"
evento = "evento"
atividades = "atividades"
submissao = "submissao"
chamadas = "chamadas"
portal = "portal"
credenciamento = "credenciamento"





# Adicionando itens de menu
Menu.add_item(main, MenuItem(
    "Dashboard",
    reverse('user:dashboard'),
    icon='fas fa-home',
    check=lambda request: rules.test_rule('is_participant_rule', request)
))



Menu.add_item(main, MenuItem(
    "Meus Trabalhos", 
    url=reverse('user:trabalho-meus_trabalhos'), 
    icon='fas fa-sticky-note',
    check=lambda request: rules.test_rule('is_participant_rule', request)
   
))

Menu.add_item(main, MenuItem(
    "Minhas Inscrições",
    url=reverse('user:minhas_inscricoes'),
    icon='fas fa-money-check',
    check=lambda request: rules.test_rule('is_user_rule', request)
))

Menu.add_item(main, MenuItem(
    "Minhas Avaliações",
    url=reverse('user:avaliacao-minhas_avaliacoes'),
    icon='fa-solid fa-folder-open',
    check=lambda request: rules.test_rule('is_evaluator_rule', request)
))

Menu.add_item(main, MenuItem(
    "Tornar-se Avaliador",
    url=reverse('user:add_avaliador'),
    icon='fas fa-check',
    check=lambda request: rules.test_rule('can_evaluate_rule', request) 
))

Menu.add_item(main, MenuItem(
    "Tornar-se Monitor",
    url=reverse('user:add_monitor'),
    icon='fas fa-user',
    check=lambda request: rules.test_rule('can_monitor_rule', request) 
))

Menu.add_item(main, MenuItem(
    "Cadastro Monitor",
    url=reverse('user:edit_monitor'),
    icon='fas fa-user',
    check=lambda request: request.user.is_authenticated and request.user.is_monitor
))

Menu.add_item(evento, MenuItem(
    "Evento",
    url=reverse('evento:evento-detalhar'),
    icon='fas fa-info',
    check=lambda request:  rules.test_rule('is_member_rule', request)
))   


Menu.add_item(evento, MenuItem(
    "Notícias",
    url=reverse('evento:noticia-list'),
    icon='fas fa-newspaper',
    check=lambda request: rules.test_rule('is_member_rule', request)
))

Menu.add_item(evento, MenuItem(
    "Chamadas",
    url=reverse('chamada:chamada-list'),
    icon='fas  fa-bullhorn ',
    check=lambda request: rules.test_rule('is_member_rule', request)
))

Menu.add_item(evento, MenuItem(
    "Atividades",
    url=reverse('atividade:atividade-list'),
    icon='fas fa-person-chalkboard',
    check=lambda request: rules.test_rule('is_member_rule', request)
))

Menu.add_item(evento, MenuItem(
    "Programação",
    url=reverse('atividade:agendamento-list'),
    icon='fas fa-calendar-days',
    check=lambda request: rules.test_rule('is_member_rule', request)
))

Menu.add_item(evento, MenuItem(
    "Inscrições",
    url=reverse('credenciamento:inscricaoevento-list'),
    icon='fas fa-user-check',
    check=lambda request: rules.test_rule('is_member_rule', request)
))

Menu.add_item(evento, MenuItem(
    "Submissões",
    url=f"{reverse('submissao:submissao-list')}?etapa=inicial",
    icon='fas fa-file-arrow-up',
    check=lambda request: rules.test_rule('is_admin_rule', request)
))

Menu.add_item(portal, MenuItem(
    "Início",
    reverse('portal:index'),
    icon='fas fa-home',
))

Menu.add_item(portal, MenuItem(
    "Programação",
    url= reverse("portal:evento-atividades"),
    icon='fas fa-home',
))

Menu.add_item(portal, MenuItem(
    "Chamada de Trabalhos",
    url= reverse("portal:evento-chamadas"),
    icon='fas fa-home',
))


Menu.add_item(portal, MenuItem(
    "Downloads",
    url= reverse("portal:evento-downloads"),
    icon='fas fa-home',
    check=lambda request: request.evento and request.evento.downloads.exists()))

Menu.add_item(portal, MenuItem(
    "Organização",
    url= reverse("portal:evento-comissoes"),
    icon='fas fa-home',
))

Menu.add_item(portal, MenuItem(
    "Area do Usuário",
    reverse('user:index'),
    icon='fas fa-home',
    check=lambda request: request.user.is_authenticated
))

Menu.add_item(portal, MenuItem(
    "Acessar",
    url=reverse('account_login'),
    icon='fas fa-home',
    check=lambda request: not request.user.is_authenticated
))
