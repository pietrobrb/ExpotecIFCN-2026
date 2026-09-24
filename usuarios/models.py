from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from core.fields import FormatStringFileUpload
from enderecos.models import Contato, Endereco
from django.utils.translation import gettext_lazy as _

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

class Vinculos(models.TextChoices):
    SERVIDOR = "Servidor IFRN", "Servidor IFRN"
    ALUNO = "Aluno IFRN", "Aluno IFRN"
    ESTUDANTE = "Estudante Externo", "Estudante Externo"
    PROFISSIONAL = "Profissional Externo", "Profissional Externo"
    OUTRO = "Outro", "Outro"



class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField(max_length=255, unique=True) 
    nome_completo = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    foto_perfil = ProcessedImageField(verbose_name=_('Foto de Perfil do Usuário: '), 
                                   upload_to=FormatStringFileUpload("usuarios/avatar/{instance.id}/{filename}"), 
                                   null=True, 
                                   blank=True,
                                   processors=[ResizeToFit(width=350, upscale=False)],
                                              format='JPEG',
                                              options={'quality': 80},
                                   )
    vinculo = models.CharField(max_length=30, choices=Vinculos.choices, default=Vinculos.OUTRO)
    instituicao = models.CharField(verbose_name=_('Instituição de Ensino '), max_length=40, blank=True)
    matricula = models.CharField(max_length=20, blank=True)
    campus = models.CharField(max_length=10, blank=True)
    curso = models.CharField(max_length=40, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    endereco = models.ForeignKey(
        Endereco,
        related_name='usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Endereço")
    )

    contatos = models.ManyToManyField(
        Contato,
        through='UsuarioContato',
        related_name='usuarios',
        verbose_name=_("Contatos")
    )

    @property
    def get_primeiro_nome(self):
        return self.nome_completo.split()[0]    

    @property
    def get_ultimo_nome(self):
        return self.nome_completo.split()[-1]    
    
    @property
    def get_email(self):
        return self.email
    
    def __str__(self) -> str:
        return self.email
    

class UsuarioContato(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usuario_contatos',
        verbose_name=_("Usuário")
    )
    contato = models.ForeignKey(
        Contato,
        on_delete=models.CASCADE,
        related_name='usuario_contatos',
        verbose_name=_("Contato")
    )

    class Meta:
        unique_together = ('usuario', 'contato')  # Garantir que cada usuário e contato apareça apenas uma vez
        verbose_name = 'Contato do Usuário'
        verbose_name_plural = 'Contatos do Usuário'
