import csv
import re

import django_tables2 as tables

from django.shortcuts import render
from django.db.models import Q

from .models import Trials, Stocks, Plots
from .forms import UploadStocksForm, TrialEntryForm, PlotEntryForm
from .tables import stockTable, plotTable, trialTable


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

def stockTableView(request):
    table = filterStockTable(request)

    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})


#Will generalize and move to other stocks
def filterStockTable(request, return_table = True):
    filter_object = Stocks.objects.filter()

    print("HERE")
    print(request.GET.keys())
    #This can for sure be a for loop,
    if 'filter' in request.GET.keys():
        query_str = request.GET['filter']
        if query_str != "":
            filter_object = filter_object.filter(Q(stock_id__icontains=query_str) | Q(family__family_id__icontains=query_str))

    if 'gens' in request.GET.keys():
        query_str = request.GET['gens']
        if query_str != "":
            query_int = int(re.sub("F", "", query_str))
            filter_object = filter_object.filter(gen_inbred_int = query_int)

    if 'sd_units' in request.GET.keys():
        query_str = request.GET['sd_units']
        if query_str != "":
            filter_object = filter_object.filter(amount_units = query_str)
    if return_table:
        if 'first_n' in request.GET.keys():
            table = stockTable(filter_object[:int(request.GET['first_n'])])
        else:
            table = stockTable(filter_object)
        return table
    else:
        return filter_object

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
    baseTable = filterStockTable(request, return_table = False)

    if request.method == 'GET':
        requestDict = request.GET
    elif request.method == 'POST':
        requestDict = request.POST

    checkKeys = [key for key in requestDict.keys() if re.match(r'^check-entry', key)]
    checkLines = [requestDict[value] for value in checkKeys] 

    tempData = []

    curPlot = int(requestDict['starting-plot']) 

    #TD -Calculate total length of nursery to get prepend digits
    if requestDict['plot-type'] == "HRs":
      rowsPerFamily = int(requestDict['row-number'])
      for stock in baseTable:
        famRowsAllocated = 0
        while famRowsAllocated < rowsPerFamily:
            #CHECK -are we in a plot id that checks could be in?
            if curPlot in range(1, len(checkLines)+1):
                newPlot = {
                    "plot_id" : "WHR24_" + str(curPlot),
                    "trial" : "WHWR24",
                    "experiment" : "Experiment",
                    "desig_text" :  checkLines[curPlot-1],
                    "entry_fixed" : False
                    } 
            else: 
                newPlot = {
                    "plot_id" : "WHR24_" + str(curPlot),
                    "source_stock" : stock,
                    "family" : stock.family,
                    "trial" : "WHR24",
                    "experiment" : "Experiment",
                    "desig_text" : stock.stock_id + "-" + str(famRowsAllocated + 1),
                    "gen_derived_int" : stock.gen_inbred_int - 1 , #think this set by option
                    "gen_inbred_int" : stock.gen_inbred_int,
                    "entry_fixed" : False
                    } 
                famRowsAllocated += 1

            tempData.append(newPlot)
            curPlot += 1 

    elif requestDict['plot-type'] == "Pots":
      potsPerStock = int(requestDict['pot-number'])
      for stock in baseTable:
        stockPotsAllocated = 0
        while stockPotsAllocated < potsPerStock:
            if potsPerStock > 1:
                new_desig_text = stock.stock_id + "-" + str(stockPotsAllocated + 1)
            else:
                new_desig_text = stock.stock_id

            newPlot = {
                "plot_id" : "WGHF1_24_" + str(curPlot),
                "source_stock" : stock,
                "family" : stock.family,
                "trial" : "WGHF1_24",
                "desig_text" : new_desig_text,
                "gen_derived_int" : stock.gen_inbred_int - 1 , #think this set by option
                "gen_inbred_int" : stock.gen_inbred_int,
                "entry_fixed" : False
                } 
            stockPotsAllocated += 1

            tempData.append(newPlot)
            curPlot += 1 



    elif requestDict['plot-type'] == "Yield":
        print("Hello")



    #Still have to submit tempData on action of a dif form

    #limited to first 10
    newPlotTable = plotTable(tempData[:10])

    if request.method == 'POST':
        #Create trial as tempData
        newTrial = {
            "trial_id" : "WGHF1_24",
            "year_text" : "2024",
            "location_text" : "LAB",
            "plot_type": "Pot", #Remember use short name here
            "status_text": "Planned"}

        #save trial row
        trialForm = TrialEntryForm(newTrial)

        #Don't start building the for loop until we verify this
        if trialForm.is_valid():
            trialForm.save()

            for plot in tempData:
                #Swap out trial field string for foreignkey
                #plot['trial'] = newTrial['trial_id']

                plotForm = PlotEntryForm(plot)

                if plotForm.is_valid():
                    plotForm.save()

                else:
                    print(trialForm.errors)
        else:
            print(trialForm.errors)

    return render(request, 'crossing/display_table.html', {"table" : newPlotTable})

def newNurseryDetailsView(request):
    print(request.GET.keys())
    if request.GET['plot-type'] == "HRs":
        return render(request, "germplasm/nurseries/nursery_headrows.html")
    elif request.GET['plot-type'] == "Pots":
        return render(request, "germplasm/nurseries/nursery_pots.html")


def checkFormsView(request):
    checkNumber = int(request.GET["check-number"])
    numberStrs = ["zed", "one", "two", "three", "four",
                  "five", "six", "seven", "eight", "nine"]

    if checkNumber < 10: #Which it should always be
        checkNumberList = []
        for i in range(1, checkNumber+1):
            checkNumberList.append(numberStrs[i])
    return render(request, "germplasm/nurseries/check_forms.html", {"check_number_list" : checkNumberList})



def plotView(request):
    return render(request, "germplasm/plots_index.html")

def plotWrapperView(request):
    #I don't think need to add CSV download - in tools view
    #Need to add CSV download
    if request.method == 'GET':
        return render(request, "germplasm/plots_table_wrapper.html")

def plotTableView(request):
    #Need to generalize this function and make it work here.
   # table = filterStockTable(request)
    table = plotTable(Plots.objects.all())
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})

def trialView(request):
    return render(request, "germplasm/trials_index.html")

def trialWrapperView(request):
    #I don't think need to add CSV download - in tools view
    #Need to add CSV download
    if request.method == 'GET':
        return render(request, "germplasm/trials_table_wrapper.html")

def trialTableView(request):
    #Need to generalize this function and make it work here.
   # table = filterStockTable(request)
    table = trialTable(Trials.objects.all())
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})
