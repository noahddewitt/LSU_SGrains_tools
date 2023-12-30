from django.urls import path

from . import views


app_name = "crossing"
urlpatterns = [
        path("", views.crossesView, name = "crosses_view"),
        path("crossesTable", views.crossesWrapperView, name = "crosses_wrapper_view"),
        path("crossesTable/tableContent", views.crossesTableView, name = "crosses_table_view"),
        path("entries", views.wcpView, name = "Entries View"),
        path("entries/entriesTable", views.wcpWrapperView, name = "entries_wrapper_view"),
        path("entries/entriesTable/tableContent", views.wcpTableView, name = "entries_table_view"),
        path("families", views.familiesView, name = "families_view"),
        path("families/familiesTable", views.familiesWrapperView, name = "families_wrapper_view"),
        path("families/familiesTable/tableContent", views.familiesTableView, name = "families_table_view"),
        path("<str:id_str>/", views.entryDetail, name = "entry_detail"),
        path("<str:id_str>/edit/", views.entryEditForm, name = "entry_edit_form"),
        ]


