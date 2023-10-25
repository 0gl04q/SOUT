from django import forms
from .models import FileXML


class FileXMLForm(forms.ModelForm):
    class Meta:
        model = FileXML
        fields = ['file_xml']

        labels = {
            "file_xml": "СОУТ файл",
        }

