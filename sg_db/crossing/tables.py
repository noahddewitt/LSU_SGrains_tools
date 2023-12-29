import django_tables2 as tables

from .models import Crosses, WCP_Entries

class crossesTable(tables.Table):
    class Meta:
        model = Crosses

class wcpTable(tables.Table):
    class Meta:
        model = WCP_Entries
        exclude = ("sample_id_text", )

