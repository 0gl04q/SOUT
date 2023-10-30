from django import forms
from .models import FileSOUT


class FileSOUTForm(forms.ModelForm):
    class Meta:
        model = FileSOUT
        fields = ['file_xml']

        labels = {
            "file_xml": "СОУТ файл",
        }

