from django import forms
from .models import FileSOUT, WorkPlace


class FileSOUTForm(forms.ModelForm):
    class Meta:
        model = FileSOUT
        fields = ['file_xml']

        labels = {
            "file_xml": "СОУТ файл",
        }


class WorkPlaceForm(forms.ModelForm):
    class Meta:
        model = WorkPlace
        fields = ['status', 'description']

        labels = {
            'status': 'Статус',
            'description': 'Описание',
        }
