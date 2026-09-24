from django.db import models
from django.utils.translation import gettext_lazy as _

class Estado(models.Model):
    nome = models.CharField(
        max_length=50
    )
    sigla = models.CharField(
        max_length=2
    )

    def __str__(self):
        return self.nome


class Cidade(models.Model):
    nome = models.CharField(
        max_length=50
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.nome

class Endereco(models.Model):
    pais = models.CharField(
        max_length=50,
        verbose_name=_("País"),
        default="Brasil"
    )
    estado = models.ForeignKey(
        Estado,
        verbose_name=_("Estado"),
        on_delete=models.PROTECT
    )
    cidade = models.ForeignKey(
        Cidade,
        verbose_name=_("Cidade"),
        on_delete=models.PROTECT
    )
    logradouro = models.CharField(
        max_length=255,
        verbose_name=_("Logradouro")
    )
    local = models.CharField(
        max_length=50,
        verbose_name=_("Local"),
        null=True,
        blank=True
    )

    def __str__(self):
        if self.local is None:
            return f"{self.logradouro}, {self.cidade}, {self.estado}, {self.pais}"
        return f"{self.local}, {self.logradouro}, {self.cidade}, {self.estado}, {self.pais}"

class Contato(models.Model):
    nome = models.CharField(
        max_length=100,
        verbose_name=_("Nome")
    )
    email = models.EmailField(
        verbose_name=_("Email")
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name=_("Telefone")
    )


