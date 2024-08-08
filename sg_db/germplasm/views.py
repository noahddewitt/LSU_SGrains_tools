import csv
import re

import decimal
from datetime import date, datetime
from io import TextIOWrapper

import django_tables2 as tables

from django.shortcuts import render
from django.db.models import Q

from .models import Trials, Stocks, Plots
from crossing.models import Families
from .forms import UploadStocksForm, TrialEntryForm, PlotEntryForm, StockEntryForm, UploadPlotsForm, UploadTrialsForm, StockUpdateAmountForm
from .tables import stockTable, plotTable, trialTable


def stockView(request):
    return render(request, "germplasm/stocks_index.html")

def stockWrapperView(request):
    if request.method == 'GET':
        return render(request, "germplasm/stocks_table_wrapper.html", {'upload_form': UploadStocksForm()})
    elif request.method == 'POST':
        Stocks_File = request.FILES["Stocks_File"]
        if 'Stocks_File' in request.FILES:
            #Sd units upload different than sd units for filtering
            stock_units = request.POST["sd_units_upload"] 

            Stocks_File = request.FILES["Stocks_File"]
            rows = TextIOWrapper(Stocks_File, encoding="utf-8", newline="")

            #This loop will ingest the CSV, do some cleaning, and output Dict
            #Use .reader instead of dictreader because use column position instead
            #All inputs should have stock id in left, amounts in right. header optional.

            new_stocks_dict = {}
            
            for row in csv.reader(rows):
                try: 
                    #Skip the header and avoid extraneous stuff in the file
                    stock_amount = float(row[1])

                    plot_bag_name = row[0]
                    plot_bag_name = plot_bag_name.upper()

                    #Because the barcodes are smaller, print without underscore
                    plot_bag_name = plot_bag_name.replace(" ", "_")

                    #Check padding with 0's 
                    if plot_bag_name[1:3] == "HR":
                        sep_index = plot_bag_name.find("_") + 1
                        row_str = plot_bag_name[sep_index:len(plot_bag_name)]

                        if len(row_str) < 4:
                            row_str = row_str.rjust(5, "0")
                            plot_bag_name = plot_bag_name[0:sep_index] + row_str

                    if Plots.objects.filter(plot_id = plot_bag_name).exists():
                        new_stocks_dict[plot_bag_name] = stock_amount
                        print(new_stocks_dict[plot_bag_name])

                    else:
                        print("ERROR: Plot ID not in DB")
                        break

                except:
                    pass

            #Check length of dict is N or N-1 of file?
            print(new_stocks_dict)
            for stock_plot_name in new_stocks_dict.keys():
                stock_amount = new_stocks_dict[stock_plot_name]

                stock_plot = Plots.objects.get(plot_id = stock_plot_name)
               
                print(stock_plot)
                print(stock_plot.family)

                if stock_units == "hds":
                    new_gen_derived = stock_plot.gen_inbred_int

                else:
                    new_gen_derived = stock_plot.gen_derived_int

                new_gen_inbred = stock_plot.gen_inbred_int + 1

                new_stock_id = "S-" + str(stock_plot.plot_id)

                new_stock = {
                        "stock_id" : new_stock_id,
                        "source_plot" : stock_plot,
                        "family" : stock_plot.family,
                        "gen_derived_int" : new_gen_derived,
                        "gen_inbred_int" : new_gen_inbred,
                        "location_text" : "",
                        "amount_decimal" : stock_amount,
                        "amount_units" : stock_units,
                        "entry_fixed" : True
                }

                form = StockEntryForm(new_stock)

                if form.is_valid():
                    form.save()
                else:
                    print(form.errors)

            return render(request, "germplasm/stocks_table_wrapper.html", {'upload_form': UploadStocksForm()})
 
def stockTableView(request):
    table = filterStockTable(request)

    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})


#Will generalize and move to other stocks
def filterStockTable(request, return_table = True):
    filter_object = Stocks.objects.filter()

    if request.method == 'GET':
        requestDict = request.GET

    elif request.method == 'POST':
        requestDict = request.POST

    #This can for sure be a for loop,
    print(requestDict)
    #Progressively add filters based on parameters
    for filter_var in requestDict.keys():
        if requestDict[filter_var] != "":
            if filter_var == "filter":
                filter_object = filter_object.filter(Q(stock_id__icontains=requestDict[filter_var]) | Q(family__family_id__icontains=requestDict[filter_var]))

            elif filter_var == "gens":
                query_int = int(re.sub("F", "", requestDict[filter_var]))
                filter_object = filter_object.filter(gen_inbred_int = query_int)

            elif filter_var == "sd_units":
                print(requestDict[filter_var])
                filter_object = filter_object.filter(amount_units = requestDict[filter_var])

    print(filter_object)

    if return_table:
        if 'first_n' in requestDict.keys():
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
    print(request)
    baseTable = filterStockTable(request, return_table = False)

    if request.method == 'GET':
        requestDict = request.GET
    elif request.method == 'POST':
        requestDict = request.POST
        print("RECEIVED A POST REQUEST")

    checkKeys = [key for key in requestDict.keys() if re.match(r'^check-entry', key)]
    checkLines = [requestDict[value] for value in checkKeys] 

    tempData = []
    
    starting_plot = int(requestDict['starting-plot']) 

    #inconsistent variable naming format in this view 
    curPlot = starting_plot

    print(requestDict.keys())
    short_year_str = requestDict['nursery-year'][2:4]

    #TD -Calculate total length of nursery to get prepend digits
    if requestDict['plot-type'] == "HRs":
      rowsPerFamily = int(requestDict['row-number'])
      for stock in baseTable:
        famRowsAllocated = 0
        while famRowsAllocated < rowsPerFamily:
            curPlotStr = "_" + str(curPlot).rjust(5, "0")

            #Are we in a plot id that checks could be in?
            #Our HR ranges are 50 wide!
            range_pos = (curPlot - starting_plot) % 50
            if range_pos in range(0, len(checkLines)):
                newPlot = {
                    "plot_id" : "WHR" + short_year_str + str(curPlotStr),
                    "trial" : requestDict['nursery-name'],
                    "experiment" : "Experiment",
                    "desig_text" :  checkLines[range_pos],
                    "entry_fixed" : False
                    } 
            else: 
                newPlot = {
                    "plot_id" : "WHR" + short_year_str + str(curPlotStr),
                    "source_stock" : stock,
                    "family" : stock.family,
                    "trial" : requestDict['nursery-name'],
                    "experiment" : "Experiment",
                    "desig_text" : stock.source_plot.desig_text + "-" + str(famRowsAllocated + 1),
                    "gen_derived_int" : stock.gen_derived_int , #This is set in *stock* logic
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
                "plot_id" : requestDict['nursery-name'] + str(curPlot),
                "source_stock" : stock,
                "family" : stock.family,
                "trial" : requestDict['nursery-name'],
                "desig_text" : new_desig_text,
                "gen_derived_int" : stock.gen_derived_int , #think this set by option
                "gen_inbred_int" : stock.gen_inbred_int,
                "entry_fixed" : False
                } 
            stockPotsAllocated += 1

            tempData.append(newPlot)
            curPlot += 1 



    elif requestDict['plot-type'] == "Yield":
      nursery_length = len(baseTable)
      nursery_pad = len(str(nursery_length))
      for stock in baseTable:
        curPlotStr = "_" + str(curPlot).rjust(nursery_pad, "0")

        #Are we in a plot id that checks could be in?
        range_pos = (curPlot - starting_plot) % int(requestDict['check-every'])

        if range_pos in range(0, len(checkLines)):
            newPlot = {
                "plot_id" : requestDict['nursery-name'] + curPlotStr,
                "trial" : requestDict['nursery-name'],
                "desig_text" :  checkLines[range_pos],
                "entry_fixed" : False
                }
        else: 
            newPlot = {
                "plot_id" : requestDict['nursery-name'] + curPlotStr,
                "source_stock" : stock,
                "family" : stock.family,
                "trial" : requestDict['nursery-name'], 
                "desig_text" : stock.source_plot.desig_text,
                "gen_derived_int" : stock.gen_derived_int, 
                "gen_inbred_int" : stock.gen_inbred_int,
                "entry_fixed" : False
                } 
        

        tempData.append(newPlot)
        curPlot += 1 


    #Still have to submit tempData on action of a dif form
    if request.method == 'GET':
    #limited to first 10
        newPlotTable = plotTable(tempData[:10])
        return render(request, 'crossing/display_table.html', {"table" : newPlotTable})

    elif request.method == 'POST':
        plot_type_dict = {"Pots" : "Pot", "Yield" : "Yield", "HRs" : "HR", "SPs" : "SP"}

        #Create trial as tempData
        newTrial = {
            "trial_id" : requestDict['nursery-name'],
            "year_text" : requestDict['nursery-year'],
            "location_text" : requestDict['nursery-loc'],
            "plot_type": plot_type_dict[requestDict['plot-type']], #Remember use short name here
            "status_text": "Planned"}

        #save trial row
        trialForm = TrialEntryForm(newTrial)

        #Don't start building the for loop until we verify this
        if trialForm.is_valid():

            #Have to save trial to allow dependent plots to be created
            trialForm.save()

            #The issue here is now it will start submitting I think.
            for plot in tempData:
                #Swap out trial field string for foreignkey
                #plot['trial'] = newTrial['trial_id']

                plotForm = PlotEntryForm(plot)

                if plotForm.is_valid():
                    plotForm.save()

                    #Update seed stock to remove seed
                    new_amount = plot.stock.amount_decimal - decimal.Decimal(requestDict['seed-amount'])
                    modStock = {"amount_decimal" : new_amount}

                    stockForm = StockUpdateAmountForm(modStock, instance = plot.stock)
                    stockForm.save()

                else:
                    print(trialForm.errors)

                    #REMOVE created trial
                    Trials.objects.filter(id=requestDict['nursery-name']).delete()

                    return render(request, 'germplasm/partials/fail_div.html')


            return render(request, 'germplasm/partials/success_div.html')
        else:
            print(trialForm.errors)
            return render(request, 'germplasm/partials/fail_div.html')

def newNurseryDetailsView(request):
    print(request.GET.keys())
    if request.GET['plot-type'] == "HRs":
        return render(request, "germplasm/nurseries/nursery_headrows.html")
    elif request.GET['plot-type'] == "Pots":
        return render(request, "germplasm/nurseries/nursery_pots.html")
    elif request.GET['plot-type'] == "Yield":
        return render(request, "germplasm/nurseries/nursery_yield.html")


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

def plotUploadView(request):
    if request.method == 'GET':
        return render(request, "germplasm/plots_manual_upload.html", {"upload_form": UploadPlotsForm()})
    elif request.method == 'POST':
        Plots_File = request.FILES["Plots_File"]
        rows = TextIOWrapper(Plots_File, encoding="utf-8", newline="")
        for row in csv.DictReader(rows):
            print(row)
            if not Plots.objects.filter(plot_id = row['plot_id']).exists():

                if row['source_stock'] != "":
                    row_stock = Stocks.objects.get(stock_id = row['source_stock'])
                else:
                    row_stock = None

                if row['family'] != "":
                    row_family = Families.objects.get(family_id = row['family'])
                else:
                    row_family = None

                row_trial = Trials.objects.get(trial_id = row['trial'])

                modRow = {'plot_id' : row['plot_id'],
                          'source_stock' : row_stock,
                          'family' : row_family,
                          'trial' : row_trial,
                          'desig_text' : row['desig_text'],
                          'gen_derived_int' : int(row['gen_derived_int']),
                          'gen_inbred_int' : int(row['gen_inbred_int']),
                          'notes_text' : row['notes_text'],
                          'entry_fixed' : True}

                form = PlotEntryForm(modRow)
                if form.is_valid():
                    form.save()
                else:
                    print(form.errors)
        return render(request, "germplasm/plots_manual_upload.html", {"upload_form": UploadPlotsForm()})


def plotWrapperView(request):
    if request.method == 'GET':
        return render(request, "germplasm/plots_table_wrapper.html")

def plotTableView(request):
    #Need to generalize this function and make it work here.
    #table = filterPlotTable(request)
    table = plotTable(filterPlotTable(request))
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})

def filterPlotTable(request):
    filter_object = Plots.objects.filter()

    if request.method == 'GET':
        requestDict = request.GET

    elif request.method == 'POST':
        requestDict = request.POST

    filter_object = Plots.objects.all()

    if 'filter' in requestDict.keys():
        query_str = requestDict['filter']
        if query_str != "":
            filter_object = filter_object.filter(Q(plot_id__icontains=query_str) | Q(trial__trial_id__icontains=query_str))
    
    return filter_object

def trialView(request):
    return render(request, "germplasm/trials_index.html")

def trialWrapperView(request):
    if request.method == 'GET':
        return render(request, "germplasm/trials_table_wrapper.html")

def trialTableView(request):
    #Need to generalize this function and make it work here.
   # table = filterStockTable(request)
    table = trialTable(Trials.objects.all())
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})

def trialUploadView(request):
    if request.method == 'GET':
        return render(request, "germplasm/trials_manual_upload.html", {"upload_form": UploadTrialsForm()})
    elif request.method == 'POST':
        Trials_File = request.FILES["Trials_File"]
        rows = TextIOWrapper(Trials_File, encoding="utf-8", newline="")
        for row in csv.DictReader(rows):
            print(row)

            row['harvest_date'] = datetime.strptime(row['harvest_date'], "%m/%d/%Y")
            row['planting_date'] = datetime.strptime(row['planting_date'], "%m/%d/%Y")

            if not Trials.objects.filter(trial_id = row['trial_id']).exists():
                form = TrialEntryForm(row)
                if form.is_valid():
                    form.save()
                else:
                    print(form.errors)

            else:
                existing_trial = Trials.objects.get(trial_id = row['trial_id'])
                form = TrialEntryForm(row, instance = existing_trial)
                form.save()

        return render(request, "germplasm/trials_manual_upload.html", {"upload_form": UploadPlotsForm()})
