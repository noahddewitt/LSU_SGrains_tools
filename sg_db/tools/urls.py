from django.urls import path

from . import views


app_name = "tools"
urlpatterns = [
       # path("", #Index view maybe?
       path('labels', views.lblView, name = "labels_view"),
       path('export/csv/<str:requested_model>', views.export_csv, name='export_csv'),
       #path('export/lbl/<str:requested_model>', views.export_labels, name='export_labels'),
       ]



