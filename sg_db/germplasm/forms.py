from django.forms import Form, ModelForm, FileField

from .models import Stocks, Plots, Trials

class UploadStocksForm(Form):
    Stocks_File = FileField(label = '')
    Stocks_File.widget.attrs.update({'class': 'file-upload'})

class PlotEntryForm(ModelForm):
    class Meta:
        model = Plots
        exclude = []

class TrialEntryForm(ModelForm):
    class Meta:
        model = Trials
        exclude = []
