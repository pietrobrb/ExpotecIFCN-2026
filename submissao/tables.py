from django.urls import reverse
import django_tables2 as tables

from chamadas.models import StatusChamada
from .models import StatusTrabalho, Submissao, Trabalho
from django.utils.html import format_html

class TrabalhosTable(tables.Table):
    autores_string = tables.Column(accessor='autores_string', verbose_name='Autores')
    
    class Meta:
        model = Trabalho
        fields = ['tipo_chamada', 'titulo', 'autores_string', 'status']
    

class SubmissaoTable(tables.Table):
    titulo = tables.Column(accessor='trabalho__titulo', verbose_name='Título do Trabalho')
    tipo_chamada = tables.Column(accessor='chamada__tipo', verbose_name='Chamada')
    autores_string = tables.Column(accessor='trabalho__autor_principal', verbose_name='Autores', orderable=True)
    etapa = tables.Column(accessor='chamada__etapa', verbose_name='Etapa')    
    avaliacoes = tables.Column(accessor='avaliacoes', verbose_name='Avaliações')
    status = tables.Column(accessor='trabalho__status', verbose_name='Status')
    nota = tables.Column(accessor='nota_final', verbose_name='Nota')
    
    
    class Meta:
        model = Submissao
        fields = ['titulo', 'autores_string', 'tipo_chamada', 'etapa',  'status', 'avaliacoes','nota']
    
    def render_etapa(self, record):
        return format_html(f'{record.chamada.get_etapa_display()} <br/> ({record.chamada.get_status_display()})')
    
    def render_avaliacoes(self, record):
        return format_html(f'<div class="text-center">{record.avaliacoes_realizadas.count()}/{record.chamada.min_avaliacoes}</div>')

    def render_autores_string(self, record):
        return format_html(f'{record.trabalho.autores_string}')