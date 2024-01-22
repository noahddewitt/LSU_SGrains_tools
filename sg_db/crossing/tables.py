import django_tables2 as tables

from .models import Crosses, WCP_Entries, Families


class wcpTable(tables.Table):
    cp_group_text = tables.columns.TemplateColumn(template_name = "crossing/partials/crossing_group_column.html")
    sample_id_text = tables.columns.TemplateColumn(template_name = "crossing/partials/sample_id_column.html")

    class Meta:
        model = WCP_Entries
        exclude = ("year_text", "source_text")

class crossesTable(tables.Table):
    status_text = tables.columns.TemplateColumn(template_name = "crossing/partials/cross_status_column.html")
    cross_date = tables.DateTimeColumn(format ='M d Y')

    #Change verbose names
    parent_one = tables.Column(verbose_name = "Female Parent")
    parent_two = tables.Column(verbose_name = "Male Parent")

    class Meta:
        model = Crosses
        exclude = ("year_text",)

class familiesTable(tables.Table):
    class Meta:
        model = Families
        exclude = ("year_text", "order_int")
