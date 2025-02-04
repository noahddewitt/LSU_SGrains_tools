from django.urls import path

from . import views


app_name = "tools"
urlpatterns = [
       # path("", #Index view maybe?
       path('labels', views.lblView, name = "labels_view"),
       path('labels/display', views.labelDisplayView, name = "display_label_view"),
       path('fieldbooks', views.fieldbookView, name = "fieldbooks_view"),
       path('fieldbooks/<str:file_str>', views.renderFieldbookView, name = 'render_fieldbook_view'),
       path('export/csv/<str:requested_model>', views.export_csv, name='export_csv'),
       path('export/csv/<str:requested_model>/<str:filter_str>', views.export_csv, name='export_csv'),
       path('export/htmx', views.htmx_csv_view, name = "htmx_csv_view"),
       #path('export/lbl/<str:requested_model>', views.export_labels, name='export_labels'),
       ]



