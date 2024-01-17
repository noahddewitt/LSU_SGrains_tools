import django_tables2 as tables
import re
import sys
import csv

from datetime import date, datetime
from io import TextIOWrapper
from functools import reduce

from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse, QueryDict, HttpResponseNotFound
from django.template import loader, RequestContext
from django.db.models import Q

from .models import WCP_Entries, Crosses, Families
from .tables import wcpTable, crossesTable, familiesTable
from .forms import WCPEntryForm, UploadWCPForm, CrossesEntryForm, UploadCrossesForm, FamiliesEntryForm
from tools.forms import TimesToPrintForm

from django.views.generic.base import View

def wcpView(request):
    return render(request, "crossing/wcp_index.html")

def wcpWrapperView(request):
    if request.method == 'GET':
        return render(request, "crossing/wcp_table_wrapper.html", {'upload_form': UploadWCPForm()})
    elif request.method == 'POST':
        WCP_Entries_File = request.FILES["WCP_Entries_File"]
        rows = TextIOWrapper(WCP_Entries_File, encoding="utf-8", newline="")
        for row in csv.DictReader(rows):
            form = WCPEntryForm(row)
            if form.is_valid():
                form.save()
            else: 
                print(form.errors)

        return render(request, "crossing/wcp_index.html")
       # return render(request, "crossing/upload_WCP_Entries.html", {"upload_form": UploadWCPForm()})

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
    print(request.method, file = sys.stderr)
    if request.method == 'GET':
        return render(request, "crossing/crosses_table_wrapper.html", {"form": UploadCrossesForm()})
    elif request.method == 'POST':
        print("TEST")
        Crosses_File = request.FILES["Crosses_File"]
        rows = TextIOWrapper(Crosses_File, encoding="utf-8", newline="")
        print("Crosses POST rquest", file = sys.stderr)
        for row in csv.DictReader(rows):
            #Create new dictionary based on dictionary defined by InterCross column names
            #Should this chunk here be moved to the model.save() function?
            print(row['crossDbId'], file = sys.stderr)
            #99 used as code for failure
            if int(row['seeds']) == 0:
                rowStatus = "Made"
            elif int(row['seeds']) == 99:
                row['seeds'] = 0
                rowStatus = "Failed"
            elif int(row['seeds']) > 0:
                rowStatus = "Set"

            crossTime =  datetime.strptime(row['timestamp'], "%Y-%m-%d_%H_%M_%S_%f")

            #TODO - Get year from two parents. 
            curYear = "2024"
            
            modRow = {'cross_id' : row['crossDbId'],
                      'year_text' : curYear,
                      'parent_one' : row['femaleObsUnitDbId'], 
                      'parent_two' : row['maleObsUnitDbId'], 
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
        table = familiesTable(Families.objects.filter(
            Q(family_id__icontains=query_str) | 
            Q(purdy_text__icontains=query_str) |
            Q(cross__cross_id__icontains=query_str) |
            Q(genes_text__icontains=query_str)))
    else:
        table = familiesTable(Families.objects.all())
    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table}) 


def entryDetail(request, id_str):
    if re.match(r'^WCP', id_str):
        curModel = WCP_Entries
        curForm = WCPEntryForm
        htmlPath = "crossing/entryDetail.html"
    elif re.match(r'^T', id_str):
        curModel = Crosses
        curForm = CrossesEntryForm
        htmlPath = "crossing/crossDetail.html"
    elif re.match(r'^LA', id_str):
        #Change this later to go to families table
        curModel = Families 
        curForm = FamiliesEntryForm
        htmlPath = "crossing/familyDetail.html"
    else:
        print(id_str)
        return HttpResponseNotFound(id_str)

    entry = get_object_or_404(curModel, pk = id_str)

    if request.method == 'GET':
        return render(request, htmlPath, {"entry": entry})
    elif request.method == 'PUT':
        print(id_str, file = sys.stderr)
        data = QueryDict(request.body).dict()
        form = curForm(data, instance = entry)
        if form.is_valid():
            form.save()
        else:
            print(form.errors, file=sys.stderr)

        return render(request, htmlPath, {"entry": entry})

def entryEditForm(request, id_str):
    if re.match(r'^WCP', id_str):
        curModel = WCP_Entries
        curForm = WCPEntryForm
    elif re.match(r'^T', id_str):
        curModel = Crosses
        curForm = CrossesEntryForm
    elif re.match(r'^LA', id_str):
        curModel = Families
        curForm = FamiliesEntryForm
    else:
        print(id_str)
        return HttpResponseNotFound(id_str)

    entry = get_object_or_404(curModel, pk = id_str)
    form = curForm(instance = entry)
    return render(request, "crossing/entryEdit.html", {"entry": entry, "form": form})

