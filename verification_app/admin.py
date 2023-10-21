from django.contrib import admin

from .models import Organisation, FileXML, WorkPlace

admin.site.register(Organisation)
admin.site.register(FileXML)
admin.site.register(WorkPlace)
