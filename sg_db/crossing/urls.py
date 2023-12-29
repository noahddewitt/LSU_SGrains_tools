from django.urls import path

from . import views


app_name = "crossing"
urlpatterns = [
        path("", views.crossesView, name = "Crosses View"),
        path("entries", views.wcpView, name = "Entries View"),
        path("entriesTable", views.wcpTableView, name = "entries_table_view"),
        path('export/csv/<str:requested_model>', views.export_csv, name='export_csv'),
        path('labels', views.lblView, name = "Labels View"),
        path("<str:wcp_id>/", views.entryDetail, name = "entry_detail"),
        path("<str:wcp_id>/edit/", views.entryEditForm, name = "entry_edit_form"),
        path("<str:cross_id>/", views.crossDetail, name = "detail"),
        ]


        #path('export/lbl/<str:requested_model>', views.export_labels, name='export_labels'),
