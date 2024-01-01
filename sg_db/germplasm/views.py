import csv
import re

import django_tables2 as tables

from django.shortcuts import render
from django.db.models import Q

from .models import Stocks
from .forms import UploadStocksForm
from .tables import stockTable


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
    filter_object = Stocks.objects.filter()

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

    tables.config.RequestConfig(request, paginate={"per_page": 15}).configure(table)
    return render(request, 'crossing/display_table.html', {"table" : table})

