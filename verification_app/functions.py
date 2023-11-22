import pandas as pd
from io import BytesIO

from datetime import date, datetime

import xml.etree.ElementTree as ET

from dataclasses import dataclass


@dataclass
class WorkPlace:
    SubUnit: str
    SOUTCardNumber: str
    Id: str
    Position: str
    WorkersQuantity: str
    Profession: str
    SheetDate: date


@dataclass
class Organization:
    name: str
    inn: int
    phone: str
    email: str


class SOUTFile:
    def __init__(self, data):
        self._doc = ET.fromstring(data)
        self._Enterprise = self._doc.find('Enterprise')
        self._WorkPlaceAttested = self._Enterprise.findall('WorkPlaceAttested')
        self.WorkPlacesInfo = [*self.__create_work_place_info(self._WorkPlaceAttested)]
        self.organization = Organization(
            name=self._Enterprise.find('Name').text,
            inn=int(self._Enterprise.find('INN').text),
            phone=self._Enterprise.find('Phone').text if self._Enterprise.find('Phone') else None,
            email=self._Enterprise.find('E-mail').text if self._Enterprise.find('E-mail') else None
        )
        self.date = datetime.strptime(self._doc.find('Date').text, '%Y-%m-%d').date()
        self.sout_id = int(self._doc.find('SoutId').text) if self._doc.find('SoutId') else None

    @staticmethod
    def __create_work_place_info(work_place_element):
        for place in work_place_element:
            sub_unit = place.find('SubUnit').text
            sout_card_number = place.find('SOUTCardNumber').text
            id_place = place.find('Id').text
            position = place.find('Position').text
            workers_quantity = place.find('WorkersQuantity').text
            profession = place.find('Profession').text if place.find('Profession').text != 'Отсутствует' else 0
            date_sout = datetime.strptime(place.find('SheetDate').text, '%Y-%m-%d').date()

            yield WorkPlace(sub_unit, sout_card_number, id_place, position, workers_quantity, profession, date_sout)


def create_xlsx(work_places):
    df = pd.DataFrame(
        {
            'Подразделение': [place.sub_unit for place in work_places],
            'Номер РМ': [place.place_id for place in work_places],
            'Наименование РМ': [place.position for place in work_places],
            'Работники': [place.workers_quantity for place in work_places],
            'Код ОК-01694': [place.profession for place in work_places]
        }
    )

    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, sheet_name='WorkPlacesInfo', index=False)
    writer._save()
    output.seek(0)

    return output
