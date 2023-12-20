import django_tables2 as tables

from .models import Crosses, WCP_Entries

class WCPTable(tables.Table):
    class Meta: #I think this has something to do with software tables on top of
        template_name = "django_tables2/bootstrap4.html"
        model = WCP_Entries

class CrossingTable(tables.Table):
    class Meta: #I think this has something to do with software tables on top of
        template_name = "django_tables2/bootstrap4.html"
        model = Crosses
