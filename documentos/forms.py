from django import forms

from core.forms import Select2Widget
from documentos.models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['descricao', 'tipo', 'file']
        widgets ={
            "tipo": Select2Widget(attrs={"data-placeholder": "----"})
        }