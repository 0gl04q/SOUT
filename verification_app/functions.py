import pandas as pd

from datetime import date, datetime

from pathlib import Path

from lxml import etree
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
            phone=self._Enterprise.find('Phone').text,
            email=self._Enterprise.find('E-mail').text
        )
        self.date = datetime.strptime(self._doc.find('Date').text, '%Y-%m-%d').date()
        self.sout_id = int(self._doc.find('SoutId').text)

    @staticmethod
    def __create_work_place_info(work_place_element):
        for place in work_place_element:
            sub_unit = place.find('SubUnit').text
            sout_card_number = place.find('SOUTCardNumber').text
            id_place = place.find('Id').text
            position = place.find('Position').text
            workers_quantity = place.find('WorkersQuantity').text
            profession = place.find('Profession').text
            date_sout = datetime.strptime(place.find('SheetDate').text, '%Y-%m-%d').date()

            yield WorkPlace(sub_unit, sout_card_number, id_place, position, workers_quantity, profession, date_sout)


def create_xlsx(work_places):
    def color_cells(val):
        status_color = {
            'Checked': 'color: white; background-color: green',
            'Except': 'color: black; background-color: yellow',
            'Not_check': 'color: black; background-color: white',
        }

        return status_color.get(val, 'color: black; background-color: white')

    df = pd.DataFrame(
        {
            'Подразделение': [place.SubUnit for place in all_work_place_organization],
            'Номер РМ': [place.Id for place in all_work_place_organization],
            'Наименование РМ': [place.Position for place in all_work_place_organization],
            'Работники': [place.WorkersQuantity for place in all_work_place_organization],
            'Код ОК-01694': [place.Profession for place in all_work_place_organization],
            'Статус': [place.Status for place in all_work_place_organization]
        }
    )

    df = df.style.map(color_cells, subset=pd.IndexSlice[:, 'Статус'])

    df.to_excel('./itg.xlsx', sheet_name='WorkPlacesInfo', index=False)


def upload_file(path):
    organization = '21782238'

    directory = f'./SOUTFile/Organizations/{organization}'

    path_list = Path(directory).glob('report*.xml')

    all_work_place_organization = []
    for path in path_list:
        sf = SOUTFile(str(path))
        check_entry(all_work_place_organization, sf.WorkPlacesInfo)
        all_work_place_organization.extend(sf.WorkPlacesInfo)

    create_xlsx(all_work_place_organization)
