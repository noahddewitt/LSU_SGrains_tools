import django_tables2 as tables

from germplasm.models import Plots

class FamilyPlotsTable(tables.Table):
 #   gen_text = tables.columns.TemplateColumn(template_name = "germplasm/partials/gen_text_column.html", verbose_name = "Gen")

    notes_text_one = tables.columns.TemplateColumn(template_name = "tools/partials/notes_column.html", verbose_name = "Notes1")
    notes_text_two = tables.columns.TemplateColumn(template_name = "tools/partials/notes_column.html", verbose_name = "Notes2")
    notes_space_text = tables.columns.TemplateColumn(template_name = "tools/partials/notes_column.html", verbose_name = "Notes3")
    notes_space_text = tables.columns.TemplateColumn(template_name = "tools/partials/notes_column.html", verbose_name = "Notes4")

    class Meta:
        model = Plots
        exclude = ("gen_derived_int", "gen_inbred_int", "entry_fixed", "source_stock", "trial", "family", "notes_text")


