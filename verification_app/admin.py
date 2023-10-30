from django.contrib import admin
from django.db.models import QuerySet
from .models import Organisation, FileSOUT, WorkPlace, DescriptionError, CHECKED

admin.site.register(Organisation)
admin.site.register(FileSOUT)
admin.site.register(DescriptionError)


@admin.register(WorkPlace)
class WorkPlaceAdmin(admin.ModelAdmin):
    list_displate = ['id', 'place_id', 'organization']
    list_filter = ['organization']
    actions = ['set_ch']

    @admin.action(description='Установить статус "Проверено"')
    def set_ch(self, request, queryset: QuerySet):
        queryset.update(status=CHECKED)
