import base64
from io import BytesIO

import qrcode

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from atividades.models import Agendamento, InscricaoAtividade
from eventos.models import Monitor

from .models import RegistroPresenca, SessaoPresenca, StatusSessaoPresenca


def atualizar_estado_sessao(sessao):
    if sessao.status == StatusSessaoPresenca.ABERTA and sessao.prazo_esgotado():
        sessao.encerrar()


@login_required
def monitor(request):
    monitor = get_object_or_404(
        Monitor,
        usuario=request.user,
        evento=request.evento,
    )

    agendamentos = (
        Agendamento.objects
        .filter(atividade__tipo__evento=request.evento)
        .select_related(
            "atividade",
            "atividade__tipo",
            "sala",
        )
        .order_by("dia", "inicio")
    )

    sessoes = SessaoPresenca.objects.filter(
        agendamento__in=agendamentos
    ).select_related(
        "agendamento__atividade",
        "agendamento__sala",
    )

    sessoes_por_agendamento = {sessao.agendamento_id: sessao for sessao in sessoes}

    atividades_monitor = []

    for agendamento in agendamentos:
        atividades_monitor.append(
            {
                "agendamento": agendamento,
                "sessao": sessoes_por_agendamento.get(agendamento.id),
            }
        )

    return render(
        request,
        "presenca/monitor.html",
        {
            "monitor": monitor,
            "atividades_monitor": atividades_monitor,
        },
    )


@login_required
def abrir_presenca(request, agendamento_id):
    monitor = get_object_or_404(
        Monitor,
        usuario=request.user,
        evento=request.evento,
    )

    agendamento = get_object_or_404(
        Agendamento.objects.select_related(
            "atividade",
            "atividade__tipo",
            "sala",
        ),
        pk=agendamento_id,
        atividade__tipo__evento=request.evento,
    )

    if request.method != "POST":
        return redirect("presenca:monitor")

    sessao, _ = SessaoPresenca.objects.get_or_create(
        agendamento=agendamento,
    )

    sessao.monitor = monitor
    sessao.abrir(validade_segundos=30)

    return redirect("presenca:monitor")


def gerar_qr_code(url):
    qr = qrcode.make(url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@login_required
def controle_sessao(request, sessao_id):
    monitor = get_object_or_404(
        Monitor,
        usuario=request.user,
        evento=request.evento,
    )

    sessao = get_object_or_404(
        SessaoPresenca.objects.select_related(
            "agendamento",
            "agendamento__atividade",
            "agendamento__sala",
        ),
        pk=sessao_id,
        monitor=monitor,
        agendamento__atividade__tipo__evento=request.evento,
    )

    atualizar_estado_sessao(sessao)

    checkin_url = None
    qr_code = None

    if sessao.status == StatusSessaoPresenca.ABERTA:
        checkin_url = (
            f"{settings.BASE_URL}/presenca/checkin/"
            f"{sessao.token_atual}/"
        )
        qr_code = gerar_qr_code(checkin_url)

    return render(
        request,
        "presenca/controle.html",
        {
            "monitor": monitor,
            "sessao": sessao,
            "checkin_url": checkin_url,
            "qr_code": qr_code,
        },
    )


@login_required
def estado_sessao(request, sessao_id):
    monitor = get_object_or_404(
        Monitor,
        usuario=request.user,
        evento=request.evento,
    )

    sessao = get_object_or_404(
        SessaoPresenca,
        pk=sessao_id,
        monitor=monitor,
        agendamento__atividade__tipo__evento=request.evento,
    )

    atualizar_estado_sessao(sessao)

    return JsonResponse(
        {
            "status": sessao.status,
            "prazo_esgotado": sessao.prazo_esgotado(),
            "todos_presentes": sessao.todos_presentes(),
        }
    )


@login_required
def checkin(request, token):
    sessao = (
        SessaoPresenca.objects.select_related(
            "agendamento",
            "agendamento__atividade",
            "agendamento__atividade__tipo",
            "agendamento__sala",
        )
        .filter(token_atual=token)
        .first()
    )

    if sessao is None:
        return render(
            request,
            "presenca/checkin.html",
            {
                "erro": (
                    "Este QR Code é inválido ou expirou. "
                    "Solicite ao monitor um QR Code atualizado."
                ),
            },
            status=400,
        )


    atualizar_estado_sessao(sessao)

    if sessao.status != StatusSessaoPresenca.ABERTA:
        return render(
            request,
            "presenca/checkin.html",
            {
                "erro": "A presença desta atividade não está aberta.",
            },
        )

    if not sessao.token_valido:
        return render(
            request,
            "presenca/checkin.html",
            {
                "erro": "Este QR Code expirou. Aguarde o monitor gerar um novo QR Code.",
            },
        )

    atividade = sessao.agendamento.atividade

    inscricao = InscricaoAtividade.objects.filter(
        atividade=atividade,
        usuario=request.user,
    ).first()

    if inscricao is None:
        return render(
            request,
            "presenca/checkin.html",
            {
                "erro": "Você não está inscrito nesta atividade.",
                "atividade": atividade,
            },
        )

    with transaction.atomic():
        sessao = SessaoPresenca.objects.select_for_update().get(pk=sessao.pk)

        atualizar_estado_sessao(sessao)

        if sessao.status != StatusSessaoPresenca.ABERTA or not sessao.token_valido:
            return render(
                request,
                "presenca/checkin.html",
                {
                    "erro": (
                        "A chamada foi encerrada ou este QR Code expirou. "
                        "Peça ao monitor para verificar a presença."
                    ),
                    "atividade": atividade,
                },
            )

        inscricao = InscricaoAtividade.objects.select_for_update().get(pk=inscricao.pk)

        registro, criado = RegistroPresenca.objects.get_or_create(
            sessao=sessao,
            inscricao=inscricao,
        )

        if not inscricao.presente:
            inscricao.presente = True
            inscricao.save(update_fields=["presente"])

    return render(
        request,
        "presenca/checkin.html",
        {
            "sucesso": True,
            "atividade": atividade,
            "registro": registro,
            "criado": criado,
        },
    )


@login_required
def renovar_presenca(request, sessao_id):
    monitor = get_object_or_404(
        Monitor,
        usuario=request.user,
        evento=request.evento,
    )

    sessao = get_object_or_404(
        SessaoPresenca,
        pk=sessao_id,
        monitor=monitor,
        agendamento__atividade__tipo__evento=request.evento,
    )

    atualizar_estado_sessao(sessao)

    if request.method != "POST":
        return redirect(
            "presenca:controle_sessao",
            sessao_id=sessao.id,
        )

    if sessao.status != StatusSessaoPresenca.ABERTA:
        return JsonResponse(
            {"erro": "A presença não está aberta."},
            status=400,
        )

    sessao.renovar_token(validade_segundos=30)

    checkin_url = (
        f"{settings.BASE_URL}/presenca/checkin/"
        f"{sessao.token_atual}/"
    )

    qr_code = gerar_qr_code(checkin_url)

    return JsonResponse(
        {
            "token": str(sessao.token_atual),
            "checkin_url": checkin_url,
            "qr_code": qr_code,
            "expira_em": sessao.token_expira_em.isoformat(),
        }
    )


@login_required
def encerrar_presenca(request, sessao_id):
    monitor = get_object_or_404(
        Monitor,
        usuario=request.user,
        evento=request.evento,
    )

    sessao = get_object_or_404(
        SessaoPresenca,
        pk=sessao_id,
        monitor=monitor,
        agendamento__atividade__tipo__evento=request.evento,
    )

    if request.method != "POST":
        return redirect(
            "presenca:controle_sessao",
            sessao_id=sessao.id,
        )

    if sessao.status != StatusSessaoPresenca.ABERTA:
        return redirect(
            "presenca:controle_sessao",
            sessao_id=sessao.id,
        )

    sessao.encerrar()

    return redirect(
        "presenca:controle_sessao",
        sessao_id=sessao.id,
    )


@login_required
def iniciar_atividade(request, sessao_id):
    monitor = get_object_or_404(
        Monitor,
        usuario=request.user,
        evento=request.evento,
    )

    sessao = get_object_or_404(
        SessaoPresenca,
        pk=sessao_id,
        monitor=monitor,
        agendamento__atividade__tipo__evento=request.evento,
    )

    if request.method == "POST":
        sessao.iniciar_atividade()

    return redirect(
        "presenca:controle_sessao",
        sessao_id=sessao.id,
    )
