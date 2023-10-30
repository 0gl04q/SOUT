from django.urls import path
from .views import UploadSOUTView, OrganizationsView, OrganizationPlacesView, WorkPlaceView, FileSOUTView, get_sout_file

urlpatterns = [
    path('', UploadSOUTView.as_view(), name='upload'),
    path('organizations', OrganizationsView.as_view(), name='organizations'),
    path('file_sout/<int:pk>', FileSOUTView.as_view(), name='file-sout'),
    path('organization_places/<int:pk>', OrganizationPlacesView.as_view(), name='organization-places'),
    path('work_place/<int:pk>', WorkPlaceView.as_view(), name='work-place'),
    path('download_sout_file/<int:pk>', get_sout_file, name='download-excel-file')
]
