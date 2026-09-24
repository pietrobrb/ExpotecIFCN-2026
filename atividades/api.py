from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Sala, Agendamento
from .serializers import SalaSerializer, AgendamentoSerializer

class SalaAPIListView(generics.ListAPIView):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer

class AgendamentoAPIListView(generics.ListAPIView):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer

@api_view(['POST'])
def criar_agendamento(request):
    sala_id = request.data.get('sala_id')
    atividade_id = request.data.get('atividade_id')
    inicio = request.data.get('inicio')
    fim = request.data.get('fim')
    
    agendamento = Agendamento(
        sala_id=sala_id,
        atividade_id=atividade_id,
        inicio=inicio,
        fim=fim
    )
    agendamento.save()
    
    serializer = AgendamentoSerializer(agendamento)
    return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
