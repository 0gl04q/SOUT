from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=500)
    inn = models.IntegerField(unique=True)
    phone = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f'{self.name}'


class WorkPlace(models.Model):
    sub_unit = models.CharField(max_length=1000)
    sout_card_number = models.CharField(max_length=50)
    place_id = models.CharField(max_length=50)
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    position = models.CharField(max_length=500)
    workers_quantity = models.IntegerField()
    profession = models.IntegerField()
    date_sout = models.DateField()

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

    status = models.CharField(
        max_length=2,
        choices=STATUSES,
        default=CREATED,
    )

    def __str__(self):
        return f'Рабочее место: {self.place_id} - {self.organization.name}'


class FileXML(models.Model):
    file_xml = models.FileField(upload_to='xml_files')
    date = models.DateField()
    sout_id = models.IntegerField(unique=True)
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)

    def __str__(self):
        return f'Файл XML: {self.sout_id} - {self.date}'
