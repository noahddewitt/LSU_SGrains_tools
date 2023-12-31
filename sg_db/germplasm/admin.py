from django.contrib import admin

# Register your models here.

from .models import Trials, Stocks, Plots

admin.site.register(Trials)
admin.site.register(Stocks)
admin.site.register(Plots)
