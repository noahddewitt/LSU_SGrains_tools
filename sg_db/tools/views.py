import csv
import re
import requests
import shutil

from datetime import date, datetime
from io import TextIOWrapper
from pathlib import Path

from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Min, Max

from django.http import HttpResponse

from .forms import UploadLabelsForm
from .tables import FamilyPlotsTable

from crossing.models import WCP_Entries, Crosses, Families
from germplasm.models import Plots, Stocks, Trials, Predictions

def lblView(request):
    if request.method == 'GET':
        return render(request, "tools/labels.html", {"label_form": UploadLabelsForm()}) #Merge?
    elif request.method == 'POST':
        #Bool field not included in post unless True
        if 'Include_Barcode' in request.POST.keys():
            include_barcode_bool = True
        else:
            include_barcode_bool = False

        times_to_print_int = int(request.POST['Times_To_Print'])
        
        Labels_File = request.FILES["Labels_File"]
        rows = TextIOWrapper(Labels_File, encoding="utf-8", newline="")
        row_list = []
        for row in csv.DictReader(rows):
           row_list.append(row)

        return(export_labels(request, "CSV", include_barcode = include_barcode_bool, times_to_print = times_to_print_int, csv_file = row_list))

#Generate PNG of label string based on labelry API
def labelDisplayView(request):
    if 'Include_Barcode' in request.POST.keys():
        include_barcode_bool = True
    else:
        include_barcode_bool = False

    times_to_print_int = int(request.POST['Times_To_Print'])
        
    Labels_File = request.FILES["Labels_File"]
    rows = TextIOWrapper(Labels_File, encoding="utf-8", newline="")
    
    requested_model = "CSV" 

    first_row = next(csv.DictReader(rows))

    zpl_str = export_labels(request, requested_model, include_barcode = include_barcode_bool,
                  include_date = True, times_to_print = times_to_print_int, 
                  csv_file = first_row, sample_first_entry = True)
    zpl_str = re.sub("\n", "", zpl_str)

    #Have to create unique file names to avoid static cache
    labl_date_string = str(datetime.now())

    lbl_path_folder = "/var/www/sg_db/static/tools/media/"
    lbl_file_name = "display_lbl" + labl_date_string + ".png"

    lbl_path = lbl_path_folder + lbl_file_name

    #Delete files if present. But I only want to do it *after* refresh.
    #Path(lbl_path).unlink(missing_ok=True)
    for file in Path(lbl_path_folder).glob("display_lbl*.png"):
        file.unlink()

    lbl_files = {'file' : zpl_str}
    #Can modify label size here
    lbl_url = 'http://api.labelary.com/v1/printers/8dpmm/labels/2.5x1/0/'
    lbl_response = requests.post(lbl_url, files = lbl_files, stream = True)

    if lbl_response.status_code == 200:
        lbl_response.raw.decode_content = True
        with open(lbl_path, 'wb') as out_file:
            shutil.copyfileobj(lbl_response.raw, out_file)
        

        return render(request, "tools/partials/label_display.html", {"label_png" : "tools/media/" + lbl_file_name})
    else:
        print('Error: ' + lbl_response.text)


def export_labels(request, requested_model, second_row_text = "", include_barcode = True,
                  include_date = True, times_to_print = 1, csv_file = None, sample_first_entry = False):

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

    if sample_first_entry == True:
        row_item = [row_items['id'], row_items['row_1'], row_items['row_2']]
        new_zpl_str = get_zpl_str(row_item, requested_model = requested_model,
                second_row_text = second_row_text, labl_date_string = labl_date_string, include_barcode = include_barcode)
        return new_zpl_str

    else:
        for row_item in row_items:
          if requested_model == "CSV":
              row_item = [row_item['id'], row_item['row_1'], row_item['row_2']]
              second_row_text = ""
          elif requested_model == "WCP_Entries":
              second_row_text = "Group"
          else:
              second_row_text = ""

          for _ in range(times_to_print):
              new_zpl_str = get_zpl_str(row_item, requested_model = requested_model, 
                      second_row_text = second_row_text, labl_date_string = labl_date_string, include_barcode = include_barcode)
              response.write(new_zpl_str)

        return response

def get_zpl_str(row_item, requested_model, second_row_text = "", labl_date_string = "", include_barcode = False):
    new_zpl_str = ""
    new_zpl_str += "^XA\n"
    new_zpl_str += "^CF0,40\n"
    new_zpl_str += "^FO10,5^GB490,3,3^FS\n"
    if requested_model in ["WCP_Entries", "CSV"]:
       new_zpl_str += "^FO15,35^FD" + row_item[0] + "^FS\n"
       new_zpl_str += "^CF0,20\n"
       new_zpl_str += "^FO16,90^FD" + row_item[1] + "^FS\n"
       new_zpl_str += "^FO16,125^FD" + second_row_text + row_item[2] + "^FS\n"
       if labl_date_string != "":
            new_zpl_str += "^FO16,160^FD" + labl_date_string + "^FS\n"
       if include_barcode == True:
            new_zpl_str += "^FO320,20^BQN,2,7,Q,7^FDQA," + row_item[0] + "^FS\n"
    new_zpl_str += "^FO10, 195^GB490,3,3^FS\n"
    new_zpl_str += "^XZ\n"

    return(new_zpl_str)

#Because htmx just does ajax requests, to do a CSV download have to redirect
def htmx_csv_view(request):
    requested_model = request.GET["requested_model"]
    filter_str = request.GET["filter"]

    #If filter box is empty
    if filter_str == "":
        csv_url = "/tools/export/csv/" + requested_model
    else:
        csv_url = "/tools/export/csv/" + requested_model + "/" + filter_str

    response = HttpResponse()
    response["HX-Redirect"] = csv_url

    return(response)

def export_csv(request, requested_model, filter_str = ""):
    response = HttpResponse(content_type='text/csv')

    if requested_model == "WCP_Entries":
            cur_model = WCP_Entries
    elif requested_model == "Crosses":
            cur_model = Crosses
    elif requested_model == "Families":
            cur_model = Families
    elif requested_model == "Plots":
            cur_model = Plots 
    elif requested_model == "Stocks":
            cur_model = Stocks 
    elif requested_model == "Trials":
            cur_model = Trials


    date_string = date.today().strftime("%b%d%y")
    file_name = requested_model + "_" + date_string + ".csv"
    response['Content-Disposition'] = 'attachment; filename="' + file_name +  '"'

    writer = csv.writer(response)

    #Gets names of all model fields -- probably better way to do this...
    field_list = []
    for field in cur_model._meta.get_fields():
        if field.concrete == True:
            field_list.append(field.name)

    writer.writerow(field_list)

    #The issue here is with get_fields getting fields from the plot instead of cross.. no idea why.
    print(filter_str)
    if filter_str != "":
        filter_object = cur_model.objects.all()
        if requested_model == "Stocks": 
            sel_rows = filter_object.filter(Q(stock_id__icontains=filter_str))
        elif requested_model == "Plots": 
            sel_rows = filter_object.filter(Q(plot_id__icontains=filter_str) | Q(trial__trial_id__icontains=filter_str))
        row_items = sel_rows.values_list(*field_list)
    else:
        row_items = cur_model.objects.all().values_list(*field_list)
            
    for row_item in row_items:
        writer.writerow(row_item)

    return response

def getScaleColor(value, max_val, min_val):
    scale_pos = ["#ffffe0", "#ebeed3", "#bec8b5", "#83948a", "#395653", "#003233"]
    scale_neg = ["#ffffe0", "#f3eccc", "#d8bfa0", "#b48166", "#803522", "#580000"]

    #I'm assuming max is not negative.
    if value >= 0:
        scaled_value = value / max_val
        scaled_index = int(round(scaled_value * 5, 0))
        hex_val = scale_pos[scaled_index]
    else:
        #Maintains negative value
        scaled_value = value / min_val
        scaled_index = int(round(scaled_value * 5, 0))
        hex_val = scale_neg[scaled_index]

    return hex_val

def fieldbookView(request):
    #The family list comes from the set of plots in the trial.
    if request.method == 'POST':
        #Don't fully understand this but Django doesn't like arrays from AJAX
        requestDict = request.POST
        selected_runs = request.POST.getlist("select_run")


    trial_str = requestDict['trial_str']

    preds_dict = {}
    max_min_dict = {}

    for run in selected_runs:
        run_vals = Predictions.objects.all().filter(run_text = run)

        run_pheno = run_vals.first().pheno_text
        preds_dict[run] = run_pheno 

        max_min = run_vals.aggregate(Max("value_decimal"), Min("value_decimal"))
        max_min_dict[run] = (max_min['value_decimal__max'],
                             max_min['value_decimal__min']) 

    trial_plots = Plots.objects.filter(trial__trial_id__icontains=trial_str) 


    #When we pull out the family dict, the queryset seems to automatically re-order it.
    #So we need to manually adjust to order
    trial_plot_families = trial_plots.values_list("plot_id", "family")
    trial_plot_families = list(trial_plot_families)

    #Default is to sort by first value in tuple. 
    #Plot IDs are generated in such a way that they sort correctly.
    trial_plot_families.sort()

    trial_family_transitions = []
    old_family = None

    for plot_family in trial_plot_families:
        plt_str = plot_family[0]
        fam_str = plot_family[1]

        #None will always be followed by a transition
        if (old_family is None) or (old_family != fam_str): 
            #Append old_family so that the transition is inclusive
            trial_family_transitions.append((plt_str, old_family,)) 
            old_family = fam_str

    #Finish up the last family
    #The reason we don't need a fam_str one too is because the for loop iterates through plots,
    #not transitions, so that when the last for loop ends the transition has already happened
    trial_family_transitions.append((plt_str, old_family,)) 

    args = {}
    args['preds'] = {}

    #Iterate through plots to find the transition points between families and plots. All available plots will be queried at once, and filtered to remove extraneous ones..
    #We store the previous plot so we can filter by a range
    prev_plt_str = None
    for plot_family in trial_family_transitions:
        plt_str = plot_family[0]
        fam_str = plot_family[1]

        #Prepare info for family details and predictions
        try:
            fam_object = Families.objects.get(pk = fam_str)
        except:
            if not fam_str is None:
                print("Error -- family " + str(fam_str) + " not found.")
                fam_str = None

        if not fam_str is None:
            #Assemble a dictionary of run:value pairs for all predictions
            pred_values_dict = {}
            for pred_run in preds_dict.keys():
                pred_object = Predictions.objects.all().filter(run_text = pred_run,
                                                              family = fam_object)


                if pred_object.exists():
                    pred_value = pred_object[0].value_decimal
                else:
                    pred_value = 0

                pred_color = getScaleColor(pred_value, 
                                           max_min_dict[pred_run][0],
                                           max_min_dict[pred_run][1])

                pred_values_dict[preds_dict[pred_run]] = [pred_value, pred_color]


            #All plots associated with trial and family
            #Select just the range defined by the last transition point and the current.
            #If the fmaily is just in this range, doesn't affect antyhing. If families are split up tho..
            family_plots = Plots.objects.all().filter(trial_id = trial_str, family_id = fam_str,
                    plot_id__range = [prev_plt_str, plt_str])

            family_plots_table = FamilyPlotsTable(family_plots) 

            #For each trial and family, there should only be one generation type
            first_family_plot = family_plots.values()[0]

            generation_str = str(first_family_plot["gen_derived_int"]) + ":" + str(first_family_plot["gen_inbred_int"])


            pred_values_dict['family_object'] = fam_object
            pred_values_dict['family_plots_table'] =  family_plots_table
            pred_values_dict['family_plots_gen'] = generation_str

            #Have to repeat if found in multiple places
            if fam_str in args['preds'].keys():
                repeat_list = [fam for fam in args['preds'].keys() if fam_str in fam]

                #Check if already repeats, and gets last iterated if so
                if len(repeat_list) == 1:
                    fam_str = fam_str + "_2"
                else:
                    repeat_list.sort()
                    last_repeat = repeat_list[len(repeat_list)-1]
                    #In 75 years I need to change 8 to 9
                    fam_str = fam_str + "_" + str(int(last_repeat[8]) + 1)

            args['preds'][fam_str] = pred_values_dict
        else:
            famless_dict = {}

            famless_plot = Plots.objects.all().filter(plot_id = prev_plt_str)
            famless_table = FamilyPlotsTable(famless_plot) 
            
            #Keys have to be unique. In the template, will test for presence
            #Of trial str as substr of family_object
            famless_dict['family_object'] = prev_plt_str
            famless_dict['family_plots_table'] =  famless_table
            famless_dict['family_plots_gen'] = ""

            #this avoids writing an empty family for the initial plot in the loop
            if prev_plt_str != None:
                args['preds'][plt_str] = famless_dict

        prev_plt_str = plt_str

    #Trial information for title page
    trial_object = Trials.objects.get(pk = trial_str)

    args['trial_info'] = {'trial_str':trial_str,
                          'trial_year': trial_object.year_text,
                          'trial_loc': trial_object.location_text,
                          'trial_type': trial_object.plot_type,
                          'fb_preds': preds_dict}

    return render(request, "tools/fieldbooks.html", args)


