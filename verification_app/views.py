import zipfile

from django.shortcuts import redirect
from django.core.files.base import ContentFile
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path

from .functions import SOUTFile, create_xlsx
from .forms import FileXMLForm
from .models import FileXML, Organisation, WorkPlace


class UploadSOUTView(CreateView):
    model = FileXML
    form_class = FileXMLForm
    template_name = 'verification_app/load_file.html'
    success_url = '/'

    def form_valid(self, form):
        instance = form.save(commit=False)

        zip_file = form.cleaned_data['file_xml']

        with zipfile.ZipFile(zip_file, 'r') as zf:
            file_name = 'report.xml'
            xml_data = zf.read(file_name)

        xml_content = ContentFile(xml_data)

        file_sout = SOUTFile(xml_data)

        if FileXML.objects.filter(sout_id=file_sout.sout_id):
            return redirect('upload')

        instance.file_xml.save(file_name, xml_content, save=False)

        self.pars_xml(instance, file_sout)

        instance.save()

        return super().form_valid(form)

    @staticmethod
    def pars_xml(instance, sout_info):

        instance.date = sout_info.date
        instance.sout_id = sout_info.sout_id

        # Находим или создаем организацию
        organization = Organisation.objects.filter(inn=sout_info.organization.inn).first()

        if organization is None:
            organization = Organisation(
                name=sout_info.organization.name,
                inn=sout_info.organization.inn,
                phone=sout_info.organization.phone,
                email=sout_info.organization.email
            )
            organization.save()

        instance.organization = organization

        # Создаем рабочие места
        work_places = sout_info.WorkPlacesInfo
        for place in work_places:
            old_work_place = WorkPlace.objects.filter(place_id=place.Id, organization=organization).first()

            new_work_place = WorkPlace(
                sub_unit=place.SubUnit,
                sout_card_number=place.SOUTCardNumber,
                place_id=place.Id,
                organization=organization,
                position=place.Position,
                workers_quantity=place.WorkersQuantity,
                profession=place.Profession,
                date_sout=place.SheetDate,
                status=WorkPlace.CREATED
            )

            if old_work_place:
                old_work_place.status = new_work_place.status = WorkPlace.WARNING
                old_work_place.save()
            else:
                new_work_place.status = WorkPlace.CHECKED

            new_work_place.save()


class OrganizationsView(ListView):
    paginate_by = 5
    model = Organisation
    template_name = 'verification_app/organizations.html'


class WorkPlacesView(ListView):
    model = WorkPlace
    template_name = 'verification_app/work_places.html'
    context_object_name = 'work_places'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        return queryset.filter(organization=pk).order_by('status')

    def get_context_data(self, *args, **kwargs):
        pk = self.kwargs.get('pk')

        context = super().get_context_data(*args, **kwargs)
        context['organization'] = Organisation.objects.get(pk=pk)

        return context


def get_sout_file(request, pk):
    work_places = WorkPlace.objects.filter(organization=pk)

    output = create_xlsx(work_places)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={escape_uri_path("SOUT-Excel.xlsx")}'

    return response
