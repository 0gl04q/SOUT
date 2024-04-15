from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=500)
    inn = models.BigIntegerField(unique=True)
    phone = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)

    class Meta:
        ordering = ('name',)
        indexes = (
            models.Index(fields=('inn',), name='inn_unique'),
            models.Index(fields=('name',), name='name_organization')
        )
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return f'{self.name}'


class FileSOUT(models.Model):
    file_xml = models.FileField(upload_to='xml_files')
    date = models.DateField()
    sout_id = models.IntegerField(null=True, blank=True)
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    work_places_count = models.IntegerField()

    class Meta:
        ordering = ('-date', 'organization')
        constraints = [
            models.UniqueConstraint(fields=['date', 'organization'], name='unique_date_organization')
        ]
        verbose_name = 'Файл СОУТ'
        verbose_name_plural = 'Файлы СОУТ'

    def __str__(self):
        return f'Файл XML: {self.organization.inn} - {self.work_places_count} РМ'


class WorkPlace(models.Model):
    CHECKED = 'CH'
    WARNING = 'WA'
    NOT_USED = 'NU'

    STATUSES = [
        (CHECKED, "Проверено"),
        (WARNING, "Предупреждение"),
        (NOT_USED, "Не используется")
    ]

    sub_unit = models.CharField(max_length=1000)
    sout_card_number = models.CharField(max_length=50)
    place_id = models.CharField(max_length=50)
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    position = models.CharField(max_length=500)
    workers_quantity = models.IntegerField()
    profession = models.IntegerField(null=True, blank=True)
    date_sout = models.DateField()
    file = models.ForeignKey(FileSOUT, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUSES, default=CHECKED)

    description = models.CharField(max_length=200, default='', blank=True)

    class Meta:
        ordering = ('date_sout',)
        indexes = (
            models.Index(fields=('file',)),
            models.Index(fields=('organization', 'status'), name='organization__status')
        )
        verbose_name = 'Рабочее место'
        verbose_name_plural = 'Рабочие места'

    def __str__(self):
        return f'Экземпляр РМ: {self.place_id} - {self.organization.name}'
