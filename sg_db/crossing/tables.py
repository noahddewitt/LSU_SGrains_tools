import django_tables2 as tables

from .models import Crosses, WCP_Entries, Families


class wcpTable(tables.Table):
    class Meta:
        model = WCP_Entries
        exclude = ("year_text", "sample_id_text", )

class crossesTable(tables.Table):
    class Meta:
        model = Crosses

class familiesTable(tables.Table):
    class Meta:
        model = Families 
