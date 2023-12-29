from django.urls import path

from . import views


app_name = "crossing"
urlpatterns = [
        path("", views.crossesView, name = "Crosses View"),
        path("crossesTable", views.crossesTableView, name = "crosses_table_view"),
        path("entries", views.wcpView, name = "Entries View"),
        path("entriesTable", views.wcpTableView, name = "entries_table_view"),
        path('export/csv/<str:requested_model>', views.export_csv, name='export_csv'),
        path('labels', views.lblView, name = "Labels View"),
        path("<str:id_str>/", views.entryDetail, name = "entry_detail"),
        path("<str:id_str>/edit/", views.entryEditForm, name = "entry_edit_form"),
        ]


        #path('export/lbl/<str:requested_model>', views.export_labels, name='export_labels'),
