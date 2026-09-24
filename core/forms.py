from functools import partial
from itertools import groupby

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django_select2.forms import (
    HeavySelect2MultipleWidget as DjangoHeavySelect2MultipleWidget,
)
from django_select2.forms import HeavySelect2Widget as DjangoHeavySelect2Widget
from django_select2.forms import (
    ModelSelect2MultipleWidget as DjangoModelSelect2MultipleWidget,
)
from django_select2.forms import ModelSelect2Widget as DjangoModelSelect2Widget
from django_select2.forms import Select2MultipleWidget as DjangoSelect2MultipleWidget
from django_select2.forms import Select2Widget as DjangoSelect2Widget

# patch FormHelper with default options
FormHelper.form_tag = False
FormHelper.include_media = False


class Select2NoMinLengthMixin:
    def build_attrs(self, base_attrs, extra_attrs=None):
        if extra_attrs is None:
            extra_attrs = {}
        extra_attrs.update({"data-minimum-input-length": 0})
        return super().build_attrs(base_attrs, extra_attrs)


class Select2Mixin:
    def build_attrs(self, base_attrs, extra_attrs=None):
        if extra_attrs is None:
            extra_attrs = {}
        extra_attrs.update(
            {
                "data-minimum-input-length": 0,
                "data-minimum-results-for-search": "Infinity",
            }
        )
        return super().build_attrs(base_attrs, extra_attrs)


class ModelSelect2MultipleWidget(
    Select2NoMinLengthMixin, DjangoModelSelect2MultipleWidget
):
    pass


class ModelSelect2Widget(Select2NoMinLengthMixin, DjangoModelSelect2Widget):
    empty_label = "Selecionar"


class Select2Widget(Select2Mixin, DjangoSelect2Widget):
    empty_label = "Selecionar"


class Select2MultipleWidget(DjangoSelect2MultipleWidget):
    empty_label = "Selecionar"


class MultipleSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple


class HeavySelect2Widget(Select2Mixin, DjangoHeavySelect2Widget):
    pass


class HeavySelect2MultipleWidget(
    Select2NoMinLengthMixin, DjangoHeavySelect2MultipleWidget
):
    pass


class DateInput(forms.TextInput):
    input_type = "date"


class MultipleSelectField(models.Field):
    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {
            "required": not self.blank,
            "label": self.verbose_name.capitalize(),
            "help_text": self.help_text,
            "choices": self.choices,
        }

        if self.has_default():
            defaults["initial"] = self.get_default()

        defaults.update(kwargs)

        return MultipleSelectFormField(**defaults)

    def get_prep_value(self, value):
        if value is None:
            return ""
        if isinstance(value, int):
            return str(value)
        else:
            ",".join(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, list):
            return ",".join(map(str, value))
        if value is None or isinstance(value, str):
            return value
        else:
            return str(value)

    def to_python(self, value):
        if value is None or isinstance(value, list):
            return value
        else:
            return [str(val) for val in str(value).split(",")]

    def from_db_value(self, value, expression, connection, context=None):
        if value is None:
            return value
        return self.to_python(value)

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self.choices and value not in self.empty_values:
            if not isinstance(value, list):
                value = [value]
            if set(dict(self.choices).keys()) & {int(val) for val in value} == {
                int(val) for val in value
            }:
                return
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )

        if value is None and not self.null:
            raise ValidationError(self.error_messages["null"], code="null")

        if not self.blank and value in self.empty_values:
            raise ValidationError(self.error_messages["blank"], code="blank")

    def contribute_to_class(self, cls, name, virtual_only=False):
        super().contribute_to_class(cls, name)

        if self.choices:
            fieldname = self.name
            choicedict = dict(self.choices)

            def func(self):
                value = getattr(self, fieldname)
                if not isinstance(value, list):
                    value = [value]
                return ", ".join([force_str(choicedict.get(i, i)) for i in value])

            setattr(cls, "get_%s_display" % fieldname, func)



class GroupedModelChoiceIterator(forms.models.ModelChoiceIterator):
    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset

        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


