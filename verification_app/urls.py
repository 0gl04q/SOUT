from django.urls import path
from .views import UploadSOUTView, OrganizationsView, WorkPlacesView, WorkPlaceView, get_sout_file

urlpatterns = [
    path('', UploadSOUTView.as_view(), name='upload'),
    path('organizations', OrganizationsView.as_view(), name='organizations'),
    path('work_places_organization/<int:pk>', WorkPlacesView.as_view(), name='work-places'),
    path('work_place/<int:pk>', WorkPlaceView.as_view(), name='work-place'),
    path('download_sout_file/<int:pk>', get_sout_file, name='download-excel-file')
]
