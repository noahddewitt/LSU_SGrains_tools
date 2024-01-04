from django.urls import path

from . import views

app_name = "germplasm"
urlpatterns = [
        path("stocks", views.stockView, name = "stocks_view"),
        path("stocks/stocksTable", views.stockWrapperView, name = "stocks_wrapper_view"),
        path("stocks/stocksTable/tableContent", views.stockTableView, name = "stocks_table_view"),
        path("stocks/genNursery", views.newNurseryView, name = "new_nursery_view"),
        path("stocks/genNursery/forms", views.newNurseryFormsView, name = "new_nursery_forms_view"),
        path("stocks/genNursery/details", views.newNurseryDetailsView, name = "new_nursery_details"),
        path("stocks/genNursery/plotTable", views.newNurseryPlotsTableView, name = "new_nursery_plots_table"),
        path("stocks/genNursery/forms/checkForms", views.checkFormsView, name = "check_forms"),

        ]
