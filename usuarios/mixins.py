from django.shortcuts import get_object_or_404
from django.urls import reverse
from documentos.models import Documento, TipoDocumento
from eventos.models import Avaliador
from submissao.models import Avaliacao, Submissao, Trabalho
from django.db.models import Q

class MeustrabalhosMixin:
    
    def get_object(self):
        self.object = get_object_or_404(Trabalho, pk=self.kwargs.get('pk'))
        return self.object
    
    def get_success_url(self):
        return reverse('user:trabalho-meus_trabalhos')
    
class MinhasSubmissoesMixin:
    
    def get_object(self):
        self.object = Submissao.objects.get(pk=self.kwargs.get('pk'))
        self.trabalho = self.object.trabalho
        if not self.object.documento:
            self.object.documento =  Documento.objects.create(
                tipo=TipoDocumento.TRABALHO,
                descricao=f'Documento associado à chamada {self.object.chamada} sem arquivo.'
            )
        return self.object
    
    def get_success_url(self):
        if self.object:
            return reverse('user:trabalho-detail', kwargs={'pk': self.object.trabalho.pk})
        return reverse('user:trabalho-meus_trabalhos')

class MinhasAvaliacoesMixin:
    def get_object(self):
        self.avaliador = Avaliador.objects.filter(usuario = self.request.user, evento = self.request.evento).first()
        self.object =  Avaliacao.objects.filter(avaliador = self.avaliador).get(pk=self.kwargs.get('pk'))
        return self.object
    
    def get_success_url(self):
        return reverse('user:avaliacao-minhas_avaliacoes')