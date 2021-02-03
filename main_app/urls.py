from django.urls import path
from main_app import views

urlpatterns = [
    path('',views.index, name='main'),
    path('search',views.index, name='search'),
    #path('<str:search>',views.index, name='search'),
    path('sources',views.DataSourceListView.as_view(), name='sources'),
    path('add_source',views.DataSourceCreateView.as_view(), name='addsource'),

    path('data_gov_details/<str:id>/',views.gov_details, name='content'),
    path('data_gov_rows/<int:id>/',views.gov_details, name='content'),
    path('searchdata_gov_details/<int:id>/',views.gov_details, name='content'),
    path('searchdata_gov_rows/<int:id>/',views.gov_details, name='content'),

    path('data_gov_preview/<str:id>/',views.data_gov_preview, name='content'),

    path('data_mos_details/<int:id>/',views.mos_details, name='content'),
    path('data_mos_rows/<int:id>/',views.mos_rows, name='content'),
    path('searchdata_mos_details/<int:id>/',views.mos_details, name='content'),
    path('searchdata_mos_rows/<int:id>/',views.mos_rows, name='content'),

    path('data_mos_download/<str:id>/',views.mos_download, name='download'),

    path('content_id/<int:id>/',views.row_info, name='content'),

    path('obrnadzor_details/<str:id>/',views.obrnadzor_details, name='obr'),
    path('searchdata_obrnadzor_details/<str:id>/',views.obrnadzor_details, name='obr_s'),
]