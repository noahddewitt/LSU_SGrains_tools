import django_tables2 as tables
import csv
import re

from datetime import date, datetime
from io import TextIOWrapper
from functools import reduce

from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse, QueryDict, HttpResponseNotFound
from django.template import loader, RequestContext
from django.db.models import Q

from .models import WCP_Entries, Crosses, Families
from .tables import wcpTable, crossesTable, familiesTable
from .forms import WCPEntryForm, UploadWCPForm, CrossesEntryForm, UploadCrossesForm, TimesToPrintForm, UploadLabelsForm

from django.views.generic.base import View

def wcpView(request):
    return render(request, "crossing/wcp_index.html")

def wcpWrapperView(request):
    if request.method == 'GET':
        return render(request, "crossing/wcp_table_wrapper.html", {'upload_form': UploadWCPForm(), 'print_form': TimesToPrintForm()})
    elif request.method == 'POST':
        if 'upload_files' in request.POST: #I'm not 100% sure why this works
            WCP_Entries_File = request.FILES["WCP_Entries_File"]
            rows = TextIOWrapper(WCP_Entries_File, encoding="utf-8", newline="")
            for row in csv.DictReader(rows):
                form = WCPEntryForm(row)
                form.save()

            return render(request, "crossing/upload_WCP_Entries.html", {"upload_form": UploadWCPForm(), 'print_form': print_form})
        elif 'download_labels' in request.POST:
            print_form = TimesToPrintForm(request.POST)
            if print_form.is_valid():
                
                return export_labels(request, requested_model = "WCP_Entries", times_to_print = print_form.cleaned_data['Times_To_Print'])

def wcpTableView(request):
    if 'filter' in request.GET.keys():
        query_str = request.GET['filter']
        print(query_str)
        table = wcpTable(WCP_Entries.objects.filter(
            Q(wcp_id__icontains=query_str) | 
            Q(desig_text__icontains=query_str) |
            Q(purdy_text__icontains=query_str) |
            Q(genes_text__icontains=query_str) |
            Q(notes_text__icontains=query_str)))
    else:
        table = wcpTable(WCP_Entries.objects.all())
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table}) 

def crossesView(request):
    return render(request, "crossing/crosses_index.html")

def crossesWrapperView(request):
    if request.method == 'GET':
        return render(request, "crossing/crosses_table_wrapper.html", {"form": UploadCrossesForm()})
    elif request.method == 'POST':
        Crosses_File = request.FILES["Crosses_File"]
        rows = TextIOWrapper(Crosses_File, encoding="utf-8", newline="")
        for row in csv.DictReader(rows):
            #Create new dictionary based on dictionary defined by InterCross column names
            if int(row['seeds']) > 0:
                rowStatus = "Set"
            else:
                rowStatus = "Made"

            crossTime =  datetime.strptime(row['timestamp'], "%Y-%m-%d_%H_%M_%S_%f")

            #UPDATE -- I think this needs to go - intercross will read in WCP_IDs
            #Okay, so I want to use human-readable desigs, but store data as Ids.
            #So I'll have to go through and get the Ids here.
            parent_one_str = WCP_Entries.objects.get(year_text = "2024", desig_text = row['femaleObsUnitDbId']).wcp_id
            parent_two_str = WCP_Entries.objects.get(year_text = "2024", desig_text = row['maleObsUnitDbId']).wcp_id


            modRow = {'cross_id' : row['crossDbId'],
                      'parent_one' : parent_one_str, 
                      'parent_two' : parent_two_str, 
                      'cross_date' : crossTime, 
                      'crosser_text' : row['person'],
                      'status_text' : rowStatus,
                      'seed_int' : int(row['seeds'])}

            #If the row already exists, update with new data. 
            if Crosses.objects.filter(cross_id = row['crossDbId']).exists():
                existing_cross = Crosses.objects.get(cross_id = row['crossDbId'])
                form = CrossesEntryForm(modRow, instance = existing_cross)
                form.save()

            else:
                form = CrossesEntryForm(modRow)

                if form.is_valid():
                    form.save()

        return render(request, "crossing/crosses_table_wrapper.html", {"form": UploadCrossesForm()})

def crossesTableView(request):
    if 'filter' in request.GET.keys():
        query_str = request.GET['filter']
        print(query_str)
        table = crossesTable(Crosses.objects.filter(
            Q(cross_id__icontains=query_str) | 
            Q(parent_one__desig_text__icontains=query_str) |
            Q(parent_two__desig_text__icontains=query_str) |
            Q(crosser_text__icontains=query_str) |
            Q(status_text__icontains=query_str)))
    else:
        table = crossesTable(Crosses.objects.all())
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table}) 

def familiesView(request):
    return render(request, "crossing/families_index.html")

def familiesWrapperView(request):
    if request.method == 'GET':
        return render(request, "crossing/families_table_wrapper.html")

def familiesTableView(request):
    if 'filter' in request.GET.keys():
        query_str = request.GET['filter']
        table = familiesTable(families.objects.filter(
            Q(family_id__icontains=query_str) | 
            Q(purdy_text__icontains=query_str) |
            Q(cross__cross_id__icontains=query_str) |
            Q(genes_text__icontains=query_str)))
    else:
        table = familiesTable(Families.objects.all())
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table}) 

def lblView(request):
    if request.method == 'GET':
        return render(request, "crossing/labels.html", {"label_form": UploadLabelsForm()}) #Merge?
    elif request.method == 'POST':
        Labels_File = request.FILES["Labels_File"]
        rows = TextIOWrapper(Labels_File, encoding="utf-8", newline="")
        row_list = []
        for row in csv.DictReader(rows):
           row_list.append(row)
        return(export_labels(request, "CSV", include_barcode = False, times_to_print = 1, csv_file = row_list))


def entryDetail(request, id_str):
    if re.match(r'^WCP', id_str):
        curModel = WCP_Entries
#        curForm = WCPEntryForm
        htmlPath = "crossing/entryDetail.html"
    elif re.match(r'^T', id_str):
        curModel = Crosses
 #       curForm = CrossesEntryForm
        htmlPath = "crossing/crossDetail.html"
    elif re.match(r'^LA', id_str):
        #Change this later to go to families table
        curModel = Families 
  #      curForm = CrossesEntryForm
        htmlPath = "crossing/familyDetail.html"
    else:
        print(id_str)
        return HttpResponseNotFound(id_str)

    entry = get_object_or_404(curModel, pk = id_str)

    if request.method == 'GET':
        return render(request, htmlPath, {"entry": entry})
    elif request.method == 'PUT':
        data = QueryDict(request.body).dict()
        form = curForm(data, instance = entry)
        if form.is_valid():
            form.save()
        return render(request, htmlPath, {"entry": entry})

def entryEditForm(request, id_str):

    if re.match(r'^WCP', id_str):
        curModel = WCP_Entries
        curForm = WCPEntryForm
    elif re.match(r'^T', id_str):
        curModel = Crosses
        curForm = CrossesEntryForm
    elif re.match(r'^LA', id_str):
        #Change this later to go to families table
        print("oh hell...")
        curModel = Crosses
        curForm = CrossesEntryForm
    else:
        print(id_str)
        return HttpResponseNotFound(id_str)

    entry = get_object_or_404(curModel, pk = id_str)
    form = curForm(instance = entry)
    return render(request, "crossing/entryEdit.html", {"entry": entry, "form": form})


def export_csv(request, requested_model):
    response = HttpResponse(content_type='text/csv')

    if requested_model == "WCP_Entries":
            cur_model = WCP_Entries
    elif requested_model == "Crosses":
            cur_model = Crosses

    date_string = date.today().strftime("%b%d%y")
    file_name = requested_model + "_" + date_string + ".csv"
    response['Content-Disposition'] = 'attachment; filename="' + file_name +  '"'

    writer = csv.writer(response)
    
    #Gets names of all model fields -- probably better way to do this...
    field_list = []
    for field in cur_model._meta.get_fields():
        if field.is_relation == False:
            field_list.append(field.name)

    writer.writerow(field_list)

    row_items = cur_model.objects.all().values_list(*field_list)
    for row_item in row_items:
        writer.writerow(row_item)

    return response

#I think this needs to be moved to its own page with options to print from model or upload csv
def export_labels(request, requested_model, include_barcode = True, 
                  include_date = True, times_to_print = 1, csv_file = None):
    response = HttpResponse(content_type = 'text/plain')

    if requested_model == "WCP_Entries":
        cur_model = WCP_Entries
    elif requested_model == "Crosses":
        cur_model = Crosses

    file_date_string = date.today().strftime("%b%d%y")
    labl_date_string = date.today().strftime("%m/%d/%Y")

    file_name = requested_model + "_lbls_" + file_date_string + ".zpl"
    response['Content-Disposition'] = 'attachment; filename="' + file_name +  '"'
    
    if requested_model != "CSV":
        row_items = cur_model.objects.all().values_list("wcp_id", "desig_text", "cp_group_text")
    else:
        row_items = csv_file 

    for row_item in row_items:
        if requested_model == "CSV":
            row_item = [row_item['id'], row_item['row_1'], row_item['row_2']]
            second_row_text = ""
        elif requested_model == "WCP_Entries":
            second_row_text = "Group"
        else:
            second_row_text = ""

        for _ in range(times_to_print):
            response.write("^XA\n")
            response.write("^CF0,40\n")
            response.write("^FO10,5^GB490,3,3^FS\n")
            if requested_model in ["WCP_Entries", "CSV"]:
                response.write("^FO15,35^FD" + row_item[0] + "^FS\n")
                response.write("^CF0,20\n")
                response.write("^FO16,90^FD" + row_item[1] + "^FS\n")
                response.write("^FO16,125^FD" + second_row_text + row_item[2] + "^FS\n")
                if include_date == True:
                    response.write("^FO16,160^FD" + labl_date_string + "^FS\n")
                if include_barcode == True:
                    response.write("^FO320,20^BQN,2,7,Q,7^FDQA," + row_item[0] + "^FS\n")
            response.write("^FO10, 195^GB490,3,3^FS\n")
            response.write("^XZ\n")

    return response


