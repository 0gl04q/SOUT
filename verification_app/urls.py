from django.urls import path
import verification_app.views as views

urlpatterns = [
    path('', views.OrganizationsView.as_view(), name='organizations'),
    path('upload', views.UploadSOUTView.as_view(), name='upload'),

    path('organizations/<int:pk>', views.OrganizationPlacesView.as_view(), name='organization-places'),

    path('file_sout/<int:pk>', views.FileSOUTView.as_view(), name='file-sout'),
    path('file_sout/<int:pk_organization>/<int:pk_file>', views.WorkPlacesFileSOUTView.as_view(), name='file-sout-places'),
    path('wa_file/<int:pk_organization>/<int:pk_file>', views.WarningView.as_view(), name='wa-file-places'),

    path('work_place/<int:pk>', views.WorkPlaceView.as_view(), name='work-place'),

    path('download_file/<int:pk>', views.get_excel_file, name='download-excel-file'),
    path('download_organization/<int:pk>', views.get_excel_organization, name='download-excel-organization')
]
