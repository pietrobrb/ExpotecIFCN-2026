from datetime import timedelta
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas
from django.utils import timezone

from atividades.models import InscricaoAtividade


def format_duration(duration):
    total_minutes = max(0, int(duration.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)
    if hours and minutes:
        return f"{hours}h {minutes:02d}min"
    if hours:
        return f"{hours}h"
    return f"{minutes}min"


def get_user_certificate_data(user, event):
    activity_certificates = list(
        InscricaoAtividade.objects.filter(
            usuario=user,
            presente=True,
            atividade__tipo__evento=event,
        )
        .select_related("atividade", "atividade__tipo")
        .order_by("atividade__titulo")
    )
    total_duration = sum(
        (inscricao.atividade.duracao for inscricao in activity_certificates),
        timedelta(),
    )
    minimum_hours = event.ch_min_certificado
    event_eligible = bool(
        activity_certificates
        and minimum_hours is not None
        and total_duration >= timedelta(hours=minimum_hours)
    )

    signature = event.certificado_signatario_assinatura
    try:
        signature_exists = bool(signature and signature.name and signature.storage.exists(signature.name))
    except (OSError, ValueError):
        signature_exists = False
    signature_configured = bool(
        event.certificado_signatario_nome.strip()
        and event.certificado_signatario_cargo.strip()
        and signature_exists
    )

    available_count = 0
    if signature_configured:
        available_count = len(activity_certificates) + int(event_eligible)

    return {
        "activity_certificates": activity_certificates,
        "total_duration": total_duration,
        "total_hours": total_duration.total_seconds() / 3600,
        "minimum_hours": minimum_hours,
        "event_eligible": event_eligible,
        "signature_configured": signature_configured,
        "available_count": available_count,
    }


def _draw_wrapped_centered(pdf, text, center_x, y, max_width, font_name="Helvetica", font_size=14, leading=22):
    pdf.setFont(font_name, font_size)
    lines = simpleSplit(text, font_name, font_size, max_width)
    for line in lines:
        pdf.drawCentredString(center_x, y, line)
        y -= leading
    return y


def _draw_image(pdf, image_field, x, y, width, height):
    with image_field.open("rb") as image_file:
        pdf.drawImage(
            ImageReader(image_file),
            x,
            y,
            width=width,
            height=height,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )


def generate_certificate_pdf(event, user, duration, activity=None):
    buffer = BytesIO()
    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height), pageCompression=1)
    pdf.setTitle("Certificado - " + (activity.titulo if activity else event.titulo))
    pdf.setAuthor(event.titulo)

    margin = 24
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    pdf.setStrokeColor(colors.HexColor("#176B75"))
    pdf.setLineWidth(2)
    pdf.roundRect(margin, margin, page_width - 2 * margin, page_height - 2 * margin, 12, fill=0, stroke=1)

    if event.logo:
        _draw_image(pdf, event.logo, 48, page_height - 105, 115, 55)

    center_x = page_width / 2
    pdf.setFillColor(colors.HexColor("#176B75"))
    pdf.setFont("Helvetica-Bold", 27)
    pdf.drawCentredString(center_x, page_height - 85, "CERTIFICADO")
    pdf.setFillColor(colors.HexColor("#4B5563"))
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(center_x, page_height - 108, f"{event.edicao} - {event.titulo} ({event.ano})")

    y = page_height - 170
    pdf.setFillColor(colors.HexColor("#374151"))
    y = _draw_wrapped_centered(
        pdf,
        "Certificamos que",
        center_x,
        y,
        page_width - 150,
        font_size=15,
    )
    pdf.setFillColor(colors.HexColor("#111827"))
    y = _draw_wrapped_centered(
        pdf,
        user.nome_completo,
        center_x,
        y - 5,
        page_width - 150,
        font_name="Helvetica-Bold",
        font_size=24,
        leading=30,
    )

    if activity:
        statement = (
            f"participou da atividade {activity.titulo}, com presença confirmada, "
            f"totalizando {format_duration(duration)}."
        )
    else:
        statement = (
            f"participou do evento {event.titulo}, cumprindo "
            f"{format_duration(duration)} em atividades com presença confirmada."
        )
    pdf.setFillColor(colors.HexColor("#374151"))
    y = _draw_wrapped_centered(
        pdf,
        statement,
        center_x,
        y - 12,
        page_width - 180,
        font_size=15,
        leading=23,
    )
    period = f"{event.dt_inicio.strftime('%d/%m/%Y')} a {event.dt_encerramento.strftime('%d/%m/%Y')}"
    _draw_wrapped_centered(
        pdf,
        f"Realizado no período de {period}.",
        center_x,
        y - 5,
        page_width - 180,
        font_size=12,
        leading=18,
    )

    signature_y = 88
    signature_width = 145
    _draw_image(
        pdf,
        event.certificado_signatario_assinatura,
        center_x - signature_width / 2,
        signature_y + 23,
        signature_width,
        45,
    )
    pdf.setStrokeColor(colors.HexColor("#6B7280"))
    pdf.setLineWidth(0.7)
    pdf.line(center_x - 105, signature_y + 20, center_x + 105, signature_y + 20)
    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(center_x, signature_y + 5, event.certificado_signatario_nome)
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(center_x, signature_y - 8, event.certificado_signatario_cargo)
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(center_x, 42, "Emitido em " + timezone.localdate().strftime("%d/%m/%Y"))

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()