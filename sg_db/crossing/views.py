import django_tables2 as tables
import csv

from datetime import date, datetime
from io import TextIOWrapper

from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse
from django.template import loader, RequestContext

from .models import WCP_Entries, Crosses
from .tables import CrossingTable, WCPTable
from .forms import WCPEntryForm, UploadWCPForm, CrossesEntryForm, UploadCrossesForm, TimesToPrintForm

from django.views.generic.base import View


def wcpView(request):
    table = WCPTable(WCP_Entries.objects.all())
    tables.config.RequestConfig(request).configure(table)

    if request.method == 'GET':
        return render(request, "crossing/wcp_index.html", {'table': table, 'upload_form': UploadWCPForm(), 'print_form': TimesToPrintForm()})
    elif request.method == 'POST':
        if 'upload_files' in request.POST: #I'm not 100% sure why this works
            WCP_Entries_File = request.FILES["WCP_Entries_File"]
            rows = TextIOWrapper(WCP_Entries_File, encoding="utf-8", newline="")
            for row in csv.DictReader(rows):
                form = WCPEntryForm(row)
                form.save()

            return render(request, "crossing/upload_WCP_Entries.html", {'table': table, "upload_form": UploadWCPForm(), 'print_form': print_form})
        elif 'download_labels' in request.POST:
            print_form = TimesToPrintForm(request.POST)
            if print_form.is_valid():
                
                return export_labels(request, requested_model = "WCP_Entries", times_to_print = print_form.cleaned_data['Times_To_Print'])

def crossesView(request):
    table = CrossingTable(Crosses.objects.all())
    tables.config.RequestConfig(request).configure(table)

    if request.method == 'GET':
        return render(request, "crossing/crosses_index.html", {'table': table, "form": UploadCrossesForm()})
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
                else: 
                    print(form.errors)

        return render(request, "crossing/crosses_index.html", {'table': table, "form": UploadCrossesForm()})

def detail(request, cross_id):
    cross = get_object_or_404(Crosses, pk = cross_id)
    return render(request, "crossing/detail.html", {"cross": cross})

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

#I did have this as a seperate url-based thing, but now I'm just calling it directly...
def export_labels(request, requested_model, times_to_print = 1):
    response = HttpResponse(content_type = 'text/plain')

    if requested_model == "WCP_Entries":
        cur_model = WCP_Entries
    elif requested_model == "Crosses":
        cur_model = Crosses

    date_string = date.today().strftime("%b%d%y")
    file_name = requested_model + "_lbls_" + date_string + ".zpl"
    response['Content-Disposition'] = 'attachment; filename="' + file_name +  '"'

    row_items = cur_model.objects.all().values_list("wcp_id", "desig_text", "cp_group_text")

    for row_item in row_items:
        for _ in range(times_to_print):
            response.write("^XA\n")
            response.write("^CF0,40\n")
            response.write("^FO10,5^GB490,3,3^FS\n")
            if(requested_model == "WCP_Entries"):
                response.write("^FO15,35^FD" + row_item[0] + "^FS\n")
                response.write("^CF0,20\n")
                response.write("^FO16,100^FD" + row_item[1] + "^FS\n")
                response.write("^FO16,150^FD" + "Group: " + row_item[2] + "^FS\n")
                response.write("^FO320,20^BQN,2,7,Q,7^FDQA," + row_item[0] + "^FS\n")
            response.write("^FO10, 195^GB490,3,3^FS\n")
            response.write("^XZ\n")

    
    return response


