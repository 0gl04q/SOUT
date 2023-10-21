from django.urls import path
from .views import UploadSOUTView, OrganizationsView, WorkPlacesView

urlpatterns = [
    path('', UploadSOUTView.as_view(), name='upload'),
    path('sout_info', OrganizationsView.as_view(), name='organizations'),
    path('sout_info/<int:pk>', WorkPlacesView.as_view(), name='work-places')
]
