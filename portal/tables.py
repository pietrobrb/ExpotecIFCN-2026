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
        horario_formatado = value.strftime('%H:%M')  # Formata para hh:mm
        return format_html(
            f"<div class='py-0 my-0'>{horario_formatado}</div><div class='xsmall'>{record.atividade.tipo}</div>"
        )

    def render_atividade(self, value, record):
        return format_html(
            f"<p class='py-0 my-0'><strong>{value}</strong><br/><small class='small'>{record.horario}</small></p>"
        )

    def render_local(self, value, record):
        return format_html(
            f"<p class='py-0 my-0 text-nowrap'><strong>Local</strong><br/><small class='small'>{value}</small></p>"
        )
    
    

   
