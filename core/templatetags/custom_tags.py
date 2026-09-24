from django import template
from django.http import HttpRequest
import rules

from usuarios.models import User
register = template.Library()

@register.filter(name='split_text')
def split_text(value):
    if not value:
        return '', ''
    
    split_index = len(value) // 2

    
    if split_index > 0 and value[split_index] != ' ':
        # Encontre o espaço mais próximo antes e depois do split_index
        left_space = value.rfind(' ', 0, split_index)
        right_space = value.find(' ', split_index)
    
        if right_space == -1:
            right_space = len(value)
        if left_space == -1:
            left_space = 0
        
        if left_space == -1 or (split_index - left_space) < (right_space - split_index):
            split_index = right_space
        else:
            split_index = left_space

    first_half = value[:split_index].strip()
    second_half = value[split_index:].strip()
    
    return first_half, second_half

@register.filter(name='split_by_index')
def split_text_by_index(value, split_point):
    """
    Divide o texto em duas partes, sem cortar palavras ao meio.
    O split_point é o índice inicial para a divisão.
    Se não encontrar um espaço, divide diretamente no meio.
    """
    if not isinstance(value, str):
        return value  # Se não for string, retorna o valor original

    if len(value) <= split_point:
        return value  # Se o texto for menor ou igual ao limite, retorna o valor original
    # Ajustar para evitar cortar palavras no meio
    split_point = int(split_point)
    if split_point > 0 and value[split_point] != ' ':
        left_space = value.rfind(' ', 0, split_point)
        right_space = value.find(' ', split_point)
        
        if left_space == -1:  # Caso não encontre um espaço à esquerda
            left_space = 0
        if right_space == -1:  # Caso não encontre um espaço à direita
            right_space = len(value)
        
        # Escolhe o espaço mais próximo para dividir, sem cortar a palavra
        if split_point - left_space <= right_space - split_point:
            split_point = left_space
        else:
            split_point = right_space

    first_half = value[:split_point].strip()

    return f"{first_half}"

