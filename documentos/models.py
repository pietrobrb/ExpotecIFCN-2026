from django.db import models

from django.utils.translation import gettext_lazy as _

from core.fields import FormatStringFileUpload

class TipoDocumento(models.TextChoices):
    ESTILHO = 'estilo', _("Estilo")
    DOWNLOAD = 'download', _("Download")
    TRABALHO = 'trabalho', _("Trabalho")
    REGRA = 'regra', _("Orientações")
    MODELO = 'modelo', _("Modelo")
    
# Create your models here.
class Documento(models.Model):
    descricao = models.CharField(
        max_length=255,
        verbose_name=_("Descrição")
    )
    file = models.FileField(
        upload_to=FormatStringFileUpload("documentos/{instance.id}/{filename}"),
        verbose_name=_("Arquivo")
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoDocumento.choices,
        verbose_name=_("Tipo de Documento")
    )

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'