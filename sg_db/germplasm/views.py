import csv
import re

import django_tables2 as tables

from django.shortcuts import render
from django.db.models import Q

from .models import Trials, Experiments, Stocks, Plots
from .forms import UploadStocksForm
from .tables import stockTable, plotTable


def stockView(request):
    return render(request, "germplasm/stocks_index.html")

def stockWrapperView(request):
    if request.method == 'GET':
        return render(request, "germplasm/stocks_table_wrapper.html", {'upload_form': UploadStocksForm()})
    elif request.method == 'POST':
        if 'upload_files' in request.POST: #I'm not 100% sure why this works
            Stocks_Entries_File = request.FILES["Stocks_Entries_File"]
            rows = TextIOWrapper(Stocks_Entries_File, encoding="utf-8", newline="")
            for row in csv.DictReader(rows):
                form = StocksEntryForm(row)
                form.save()

            return render(request, "crossing/upload_Stocks_Entries.html", {"upload_form": UploadStocksForm(), 'print_form': print_form})
      #  elif 'download_labels' in request.POST:
       #     print_form = TimesToPrintForm(request.POST)
        #    if print_form.is_valid():

         #       return export_labels(request, requested_model = "WCP_Entries", times_to_print = print_form.cleaned_data['Times_To_Print'])


def stockTableView(request):
    table = filterStockTable(request)
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})


#Will generalize and move to other stocks
def filterStockTable(request):
    filter_object = Stocks.objects.filter()

    #This can for sure be a for loop,
    if 'filter' in request.GET.keys():
        query_str = request.GET['filter']
        filter_object = filter_object.filter(Q(stock_id__icontains=query_str) | Q(family__family_id__icontains=query_str))

    if 'gens' in request.GET.keys():
        query_str = request.GET['gens']
        query_int = int(re.sub("F", "", query_str))
        filter_object = filter_object.filter(gen_inbred_int = query_int)

    if 'sd_units' in request.GET.keys():
        query_str = request.GET['sd_units']
        filter_object = filter_object.filter(amount_units = query_str)

    table = stockTable(filter_object)
    return table

#In most cases this will be fine, but need to add column
#To seed stock for selected
def newNurseryView(request):

    stockFilters = request.GET
    print("hey")
    print(stockFilters)

    #Logic here for importing stocks and making trials...
    #Need to pass on dictionary of GET request to subsequent views...
    if request.method == 'GET':
        return render(request, "germplasm/nursery_creation.html", { 'stock_filters' : stockFilters} )#, {"form": TrialDetailsForm()})

def newNurseryFormsView(request):
    if request.method == 'GET':
        stockFilters = request.GET
        #I think that this is a reasonable way to do this. 
        return render(request, "germplasm/nursery_creation_forms.html", {'upload_form': UploadStocksForm(), 'stock_filters' : stockFilters})

def newNurseryPlotsTableView(request):
    #baseTable = filterStockTable(request)
    baseTable = Stocks.objects.all()

    print(baseTable)

    tempData = [
            {"stock_id" : "LA151", "source_plot" : "", "family" : "LA24001",
                "gen_derived_int" : 2, "gen_inbred_int" : 3, "location_text" : "hey", "amount_decimal" : 10.0, "amount_units" : "sds", "entry_fixed" : False}

            ]

    tempData = []

    rowsPerFamily = 1

    for stock in baseTable:
        for i in range(1, rowsPerFamily+1):
            print(stock)
            newPlot = {
                    "plot_id" : stock.stock_id + "-" + str(i),
                    "source_stock" : stock,
                    "family" : stock.family,
                    "trial" : "Trial",
                    "experiment" : "Experiment",
                    "desig_text" : stock.stock_id + "-" + str(i),
                    "gen_derived_int" : stock.gen_derived_int + 1, #think this set by option
                    "gen_inbred_int" : stock.gen_inbred_int,
                    "entry_fixed" : False
                    } 
            tempData.append(newPlot)

    print(tempData)

    table = plotTable(tempData)


#    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})

def newNurseryDetailsView(request):
    print(request.GET.keys())
    if request.GET['plot-type'] == "HRs":
        return render(request, "germplasm/nurseries/nursery_headrows.html")
    elif request.GET['plot-type'] == "Pots":
        return render(request, "germplasm/nurseries/nursery_headrows.html")



