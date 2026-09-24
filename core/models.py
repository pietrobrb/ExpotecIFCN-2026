from django import forms
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def get_hoje():
    return timezone.now().date()

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="deleted")[0]

def validate_future_date(value):
    if value < get_hoje():
        raise forms.ValidationError('A data e hora devem ser no futuro.')

class Shift(models.TextChoices):
    DAWN = "Dawn", _("Dawn")
    MORNING = "Morning", _("Morning")
    AFTERNOON = "Afternoon", _("Afternoon")
    EVENING = "Evening", _("Evening")


class TimestampedModel(models.Model):
    datetime = models.DateTimeField(
        _("Data e Hora"), auto_now_add=False, editable=False
    )
    week_day = models.IntegerField(_("Dia da Semana"), editable=False)
    week = models.IntegerField(_("Semana"), editable=False)
    date = models.DateField(_("Data"), editable=False)
    month = models.IntegerField(_("Mês"), editable=False)
    year = models.IntegerField(_("Ano"), editable=False)
    hour = models.IntegerField(_("Hora"), editable=False)
    shift = models.CharField(_("Turno"), max_length=20, choices=Shift.choices)

    class Meta:
        abstract = True
        verbose_name = _("Data")
        verbose_name_plural = _("Datas")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datetime = timezone.now().replace(minute=0, second=0, microsecond=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_timestamp_fields()
        super().save(*args, **kwargs)

    def set_timestamp_fields(self):
        self.week_day = self.datetime.weekday()
        self.week = self.datetime.isocalendar()[1]
        self.date = self.datetime.date()
        self.month = self.datetime.month
        self.year = self.datetime.year
        self.hour = self.datetime.hour
        if self.hour < 6:
            self.shift = Shift.DAWN
        elif self.hour < 12:
            self.shift = Shift.MORNING
        elif self.hour < 18:
            self.shift = Shift.AFTERNOON
        else:
            self.shift = Shift.EVENING

    def __str__(self) -> str:
        return f"{self.date} - {self.hour}h - {self.shift}"


class CreationTimestampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("Criado em"), null=True)
    created_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Criado por"),
        on_delete=models.SET(get_sentinel_user),
        null=True,
        related_name="%(class)s_created_by",
    )

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class UpdateTimestampedModel(models.Model):
    updated_at = models.DateTimeField(verbose_name=_("Atualizado em"), null=True)
    updated_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Atualizado por"),
        on_delete=models.SET(get_sentinel_user),
        null=True,
        related_name="%(class)s_updated_by",
    )

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseModel(models.Model):
    class Meta:
        abstract = True


class BaseTimestampedModel(BaseModel, CreationTimestampedModel, UpdateTimestampedModel):
    class Meta:
        abstract = True
