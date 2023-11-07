import zipfile

from django.shortcuts import redirect
from django.core.files.base import ContentFile
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from django.db.models import Q, F, Count, OuterRef, Subquery, Max

from .functions import SOUTFile, create_xlsx
from .forms import FileSOUTForm
from .models import FileSOUT, Organisation, WorkPlace, CHECKED, WARNING, CREATED, ERROR


class UploadSOUTView(CreateView):
    model = FileSOUT
    form_class = FileSOUTForm
    template_name = 'verification_app/load_file.html'
    success_url = '/'

    def form_valid(self, form):
        instance = form.save(commit=False)

        # Расшифровываем полученный файл
        zip_file = form.cleaned_data['file_xml']

        file_name = 'report.xml'

        with zipfile.ZipFile(zip_file, 'r') as zf:
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
            new_work_place = WorkPlace(
                sub_unit=place.SubUnit,
                sout_card_number=place.SOUTCardNumber,
                place_id=place.Id,
                organization=organization,
                position=place.Position,
                workers_quantity=place.WorkersQuantity,
                profession=place.Profession,
                date_sout=place.SheetDate,
                file=instance
            )

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
    template_name = 'verification_app/work_places_organization.html'
    context_object_name = 'work_places'

    def get_queryset(self):
        pk = self.kwargs['pk']

        queryset = get_organization_places_queryset(pk)
        return queryset

    def get_context_data(self, *args, **kwargs):
        pk = self.kwargs['pk']

        context = super().get_context_data(*args, **kwargs)
        context['organization'] = Organisation.objects.get(pk=pk)
        context['total_places'] = WorkPlace.objects.filter(organization=pk).count()
        return context


def get_organization_places_queryset(pk):
    latest_dates = WorkPlace.objects.filter(
        organization=pk,
        place_id=OuterRef('place_id')
    ).values('place_id').annotate(
        max_date=Max('file__date')
    ).values('max_date')

    queryset = WorkPlace.objects.filter(
        organization=pk
    ).annotate(
        max_date=Subquery(latest_dates)
    ).filter(
        file__date=F('max_date')
    ).order_by('place_id', '-file__date')

    return queryset


class WorkPlaceView(DetailView):
    model = WorkPlace
    template_name = 'verification_app/work_place.html'


class FileSOUTView(ListView):
    model = FileSOUT
    template_name = 'verification_app/files_sout.html'
    context_object_name = 'files_sout'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        file_queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        return file_queryset.filter(organization=pk).order_by('-date')

    def get_context_data(self, *args, **kwargs):
        pk = self.kwargs.get('pk')

        context = super().get_context_data(*args, **kwargs)
        context['organization'] = Organisation.objects.get(pk=pk)
        context['files_sout'] = zip(context['files_sout'], self.sum_repeat())

        return context

    def sum_repeat(self):
        all_repeat = []

        for file in self.get_queryset():
            places_id = WorkPlace.objects.filter(organization=self.kwargs.get('pk')).values('place_id').annotate(
                place_count=Count('place_id')).filter(place_count__gt=1).values('place_id')

            queryset = WorkPlace.objects.filter(file=file, place_id__in=places_id).count()
            all_repeat.append(queryset)

        return all_repeat


class WorkPlacesFileSOUTView(ListView):
    model = WorkPlace
    template_name = 'verification_app/work_places_file.html'
    context_object_name = 'work_places'

    def get_queryset(self):
        pk_file = self.kwargs['pk_file']
        pk_organization = self.kwargs['pk_organization']
        queryset = WorkPlace.objects.filter(file=pk_file, organization=pk_organization)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['organization'] = Organisation.objects.get(pk=self.kwargs['pk_organization'])
        context['file'] = FileSOUT.objects.get(pk=self.kwargs['pk_file'])
        return context


class WarningView(ListView):
    model = WorkPlace
    template_name = 'verification_app/warning_places.html'
    context_object_name = 'work_places'

    def get_queryset(self):
        queryset = self.warning_queryset()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['organization'] = Organisation.objects.get(pk=self.kwargs['pk_organization'])
        context['file'] = FileSOUT.objects.get(pk=self.kwargs['pk_file'])
        context['wa_work_places'] = {
            place.place_id: [
                pl for pl in WorkPlace.objects.filter(
                    organization=context['organization'],
                    place_id=place.place_id
                ).exclude(file=place.file)
            ] for place in self.get_queryset()
        }
        return context

    def warning_queryset(self):
        pk_file = self.kwargs['pk_file']
        pk_organization = self.kwargs['pk_organization']

        places_id = WorkPlace.objects.filter(
            organization=pk_organization
        ).values('place_id').annotate(
            place_count=Count('place_id')
        ).filter(place_count__gt=1).values('place_id')

        queryset = WorkPlace.objects.filter(file=pk_file, place_id__in=places_id)

        return queryset


def get_excel_file(request, pk):
    work_places = WorkPlace.objects.filter(file=pk)

    organization = FileSOUT.objects.get(pk=pk).organization.name

    output = create_xlsx(work_places)

    response = HttpResponse(output.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={escape_uri_path(f"{organization}_SOUT.xlsx")}'

    return response


def get_excel_organization(request, pk):
    work_places = get_organization_places_queryset(pk)

    organization = Organisation.objects.get(pk=pk)

    output = create_xlsx(work_places)

    response = HttpResponse(output.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={escape_uri_path(f"{organization}_SOUT.xlsx")}'

    return response
