from django.urls import path

from . import views

app_name = "germplasm"
urlpatterns = [
        path("", views.plotView, name = "plots_view"),
        path("plotsUpload", views.plotUploadView, name = "plots_manual_upload"),
        path("plotsTable", views.plotWrapperView, name = "plots_wrapper_view"),
        path("plotsTable/tableContent", views.plotTableView, name = "plots_table_view"),
        path("stocks", views.stockView, name = "stocks_view"),
        path("stocks/stocksTable", views.stockWrapperView, name = "stocks_wrapper_view"),
        path("stocks/stocksTable/tableContent", views.stockTableView, name = "stocks_table_view"),
        path("stocks/genNursery", views.newNurseryView, name = "new_nursery_view"),
        path("stocks/genNursery/forms", views.newNurseryFormsView, name = "new_nursery_forms_view"),
        path("stocks/genNursery/details", views.newNurseryDetailsView, name = "new_nursery_details"),
        path("stocks/genNursery/plotTable", views.newNurseryPlotsTableView, name = "new_nursery_plots_table"),
        path("stocks/genNursery/forms/checkForms", views.checkFormsView, name = "check_forms"),
        path("trials", views.trialView, name = "trials_view"),
        path("trials/trialsUpload", views.trialUploadView, name = "trials_manual_upload"),
        path("trials/trialsTable", views.trialWrapperView, name = "trials_wrapper_view"),
        path("trials/trialsTable/tableContent", views.trialTableView, name = "trials_table_view"),
        path("predictions", views.predictionsView, name = "predictions_view"),
        path("predictions/predictionsUpload", views.predictionsUploadView, name = "predictions_manual_upload"),
        path("predictions/predictionsTable", views.predictionsWrapperView, name = "predictions_wrapper_view"),
        path("predictions/predictionsTable/predictionsContent", views.predictionsTableView, name = "predictions_table_view"),
        path("predictions/predictionsTable/predictionsContent/<str:trial_filter>", views.predictionsTableView, name = "predictions_table_view"),

        ]
