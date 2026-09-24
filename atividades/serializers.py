from rest_framework import serializers
from .models import Sala, Agendamento

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ['id', 'nome', 'capacidade']

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = ['id', 'sala', 'atividade', 'inicio', 'fim']
