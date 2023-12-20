from django.urls import path

from . import views


app_name = "crossing"
urlpatterns = [
        path("", views.crossesView, name = "Crosses View"),
        path("entries", views.wcpView, name = "Entries View"),
        path('export/csv/<str:requested_model>', views.export_csv, name='export_csv'),
        #path('export/lbl/<str:requested_model>', views.export_labels, name='export_labels'),
        path("<str:cross_id>/", views.detail, name = "detail"),
        ]
