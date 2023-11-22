from django.db import models

CREATED = 'CR'
CHECKED = 'CH'
WARNING = 'WA'
ERROR = 'ER'

STATUSES = [
    (CREATED, "Создано"),
    (CHECKED, "Проверено"),
    (WARNING, "Предупреждение"),
    (ERROR, "Ошибка")
]

WA_REPEAT = 'RE'
CH_CHECKED = 'CH'

DESCRIPTIONS = [
    (WA_REPEAT, 'Повтор'),
    (CH_CHECKED, 'Без ошибок')
]


class Organisation(models.Model):
    name = models.CharField(max_length=500)
    inn = models.BigIntegerField(unique=True)
    phone = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return f'{self.name}'


class FileSOUT(models.Model):
    file_xml = models.FileField(upload_to='xml_files')
    date = models.DateField()
    sout_id = models.IntegerField(null=True)
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    work_places_count = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'organization'], name='unique_date_organization')
        ]

    def __str__(self):
        return f'Файл XML: {self.organization.inn} - {self.work_places_count} РМ'


class WorkPlace(models.Model):
    sub_unit = models.CharField(max_length=1000)
    sout_card_number = models.CharField(max_length=50)
    place_id = models.CharField(max_length=50)
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    position = models.CharField(max_length=500)
    workers_quantity = models.IntegerField()
    profession = models.IntegerField()
    date_sout = models.DateField()
    file = models.ForeignKey(FileSOUT, on_delete=models.CASCADE)

    def __str__(self):
        return f'Рабочее место: {self.place_id} - {self.organization.name}'

    def get_repeat_query_set(self, ):
        return self.objects.filter()
