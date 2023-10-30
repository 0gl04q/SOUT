import zipfile

from django.shortcuts import redirect
from django.core.files.base import ContentFile
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from django.db.models import Q

from .functions import SOUTFile, create_xlsx
from .forms import FileSOUTForm
from .models import FileSOUT, Organisation, WorkPlace, DescriptionError, CHECKED, WARNING, CREATED


class UploadSOUTView(CreateView):
    model = FileSOUT
    form_class = FileSOUTForm
    template_name = 'verification_app/load_file.html'
    success_url = '/'

    def form_valid(self, form):
        instance = form.save(commit=False)

        # Расшифровываем полученный файл
        zip_file = form.cleaned_data['file_xml']

        with zipfile.ZipFile(zip_file, 'r') as zf:
            file_name = 'report.xml'
            xml_data = zf.read(file_name)

        # Получаем XML
        xml_content = ContentFile(xml_data)

        # Парсим XML в обьект и проверяем есть ли такой файл
        file_sout = SOUTFile(xml_data)

        if FileSOUT.objects.filter(sout_id=file_sout.sout_id):
            return redirect('upload')

        # Сохраняем файл
        instance.file_xml.save(file_name, xml_content, save=False)

        # Разбираем XML
        self.pars_xml(instance, file_sout)

        return super().form_valid(form)

    @staticmethod
    def pars_xml(instance, sout_info):

        instance.date = sout_info.date
        instance.sout_id = sout_info.sout_id
        instance.work_places_count = len(sout_info.WorkPlacesInfo)

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

        instance.save()

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
                file=instance,
                status=CREATED
            )

            if old_work_place:
                new_work_place.status = WARNING
                err_repeat = DescriptionError.objects.get(description='Повтор')

                new_work_place.descriptions.add(err_repeat)
            else:
                new_work_place.status = CHECKED

            new_work_place.save()


class OrganizationsView(ListView):
    paginate_by = 10
    model = Organisation
    template_name = 'verification_app/organizations.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = Organisation.objects.filter(
                Q(name__icontains=query) | Q(inn__icontains=query)
            )
            return object_list
        return Organisation.objects.all()


class OrganizationPlacesView(ListView):
    model = WorkPlace
    template_name = 'verification_app/organization_places.html'
    context_object_name = 'work_places'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        return queryset.filter(organization=pk).order_by('-status', 'place_id')

    def get_context_data(self, *args, **kwargs):
        pk = self.kwargs.get('pk')

        context = super().get_context_data(*args, **kwargs)
        context['organization'] = Organisation.objects.get(pk=pk)

        return context


class WorkPlaceView(DetailView):
    model = WorkPlace
    template_name = 'verification_app/work_place.html'


class FileSOUTView(ListView):
    model = FileSOUT
    template_name = 'verification_app/files_sout.html'
    context_object_name = 'files_sout'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        return queryset.filter(organization=pk).order_by('-date')

    def get_context_data(self, *args, **kwargs):
        pk = self.kwargs.get('pk')

        context = super().get_context_data(*args, **kwargs)
        context['organization'] = Organisation.objects.get(pk=pk)

        return context


def get_sout_file(request, pk):
    work_places = WorkPlace.objects.filter(organization=pk)

    inn_organization = Organisation.objects.get(pk=pk).inn

    output = create_xlsx(work_places)

    response = HttpResponse(output.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={escape_uri_path(f"{inn_organization}_SOUT.xlsx")}'

    return response
