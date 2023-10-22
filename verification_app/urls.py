from django.urls import path
from .views import UploadSOUTView, OrganizationsView, WorkPlacesView, get_sout_file

urlpatterns = [
    path('', UploadSOUTView.as_view(), name='upload'),
    path('sout_info', OrganizationsView.as_view(), name='organizations'),
    path('sout_info/<int:pk>', WorkPlacesView.as_view(), name='work-places'),
    path('download_sout_file/<int:pk>', get_sout_file, name='download-excel-file')
]
