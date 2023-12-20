from django.contrib import admin

# Register your models here.

from .models import WCP_Entries, Crosses

admin.site.register(WCP_Entries)
admin.site.register(Crosses)
