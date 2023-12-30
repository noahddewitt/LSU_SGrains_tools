import csv

from datetime import date, datetime
from io import TextIOWrapper

from django.shortcuts import render

from django.http import HttpResponse

from .forms import UploadLabelsForm

from crossing.models import WCP_Entries, Crosses, Families

def lblView(request):
    if request.method == 'GET':
        return render(request, "tools/labels.html", {"label_form": UploadLabelsForm()}) #Merge?
    elif request.method == 'POST':
        Labels_File = request.FILES["Labels_File"]
        rows = TextIOWrapper(Labels_File, encoding="utf-8", newline="")
        row_list = []
        for row in csv.DictReader(rows):
           row_list.append(row)
        return(export_labels(request, "CSV", include_barcode = False, times_to_print = 1, csv_file = row_list))

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


def export_csv(request, requested_model):
    response = HttpResponse(content_type='text/csv')

    if requested_model == "WCP_Entries":
            cur_model = WCP_Entries
    elif requested_model == "Crosses":
            cur_model = Crosses
    elif requested_model == "Families":
            cur_model = Families

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


