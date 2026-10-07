from django.urls import reverse
import django_tables2 as tables
from django.utils.html import format_html

from atividades.models import Agendamento

class PortalAgendamentoTable(tables.Table):
    horario = tables.Column(accessor="inicio", verbose_name="Horário", orderable=False)
    atividade = tables.Column(accessor="atividade__titulo", verbose_name="Atividade", orderable=False)
    local = tables.Column(
        accessor="sala__nome", 
        verbose_name="Local", 
        orderable=False,  
        attrs={
            "td": {"style": "width: 150px;"} 
        })
    
    class Meta:
        model = Agendamento
        fields = (
            "horario",
            "atividade",
            "local",
        )
        show_header = False

    
    def render_horario(self, value, record):
        return format_html(
            "<div class='py-0 my-0'>{}</div><div class='xsmall'>{}</div>",
            value.strftime('%H:%M'), record.atividade.tipo,
        )

    def render_atividade(self, value, record):
        return format_html(
            "<p class='py-0 my-0'><strong>{}</strong><br/><small class='small'>{}</small></p>",
            value, record.horario,
        )

    def render_local(self, value, record):
        return format_html(
            "<p class='py-0 my-0 text-nowrap'><strong>Local</strong><br/><small class='small'>{}</small></p>",
            value,
        )
