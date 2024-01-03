import django_tables2 as tables

from .models import Plots, Stocks

class stockTable(tables.Table):
    gen_text = tables.columns.TemplateColumn(template_name = "germplasm/partials/gen_text_column.html", verbose_name = "Gen")
    seed_text = tables.columns.TemplateColumn(template_name = "germplasm/partials/seed_text_column.html", verbose_name = "Amount")

    class Meta:
        model = Stocks 
        exclude = ("gen_derived_int", "gen_inbred_int", "amount_decimal", "amount_units",)

class plotTable(tables.Table):
    class Meta:
        model = Plots

