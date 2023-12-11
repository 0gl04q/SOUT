from django.contrib import admin
from .models import Organisation, FileSOUT, WorkPlace

admin.site.register(Organisation)
admin.site.register(FileSOUT)


@admin.register(WorkPlace)
class WorkPlaceAdmin(admin.ModelAdmin):
    list_displate = ['id', 'place_id', 'organization']
    list_filter = ['file']

