from django.urls import path

from . import views

app_name = "germplasm"
urlpatterns = [
        path("stocks", views.stockView, name = "stocks_view"),
        path("stocks/stocksTable", views.stockWrapperView, name = "stocks_wrapper_view"),
        path("stocks/stocksTable/tableContent", views.stockTableView, name = "stocks_table_view"),
        path("stocks/genNursery", views.newNurseryView, name = "new_nursery_view"),

        ]
