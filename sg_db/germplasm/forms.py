from django.forms import Form, ModelForm, FileField

from .models import Stocks, Plots, Trials

class PlotEntryForm(ModelForm):
    class Meta:
        model = Plots
        exclude = []

class StockEntryForm(ModelForm):
    class Meta:
        model = Stocks
        exclude = []

class StockUpdateAmountForm(ModelForm):
    class Meta:
        model = Stocks
        fields = ["amount_decimal"]

class TrialEntryForm(ModelForm):
    class Meta:
        model = Trials
        fields = ["trial_id", "year_text", "location_text", "plot_type", "planting_date", "harvest_date", "status_text"]
        exclude = []

class UploadStocksForm(Form):
    Stocks_File = FileField(label = '')
    Stocks_File.widget.attrs.update({'class': 'file-upload'})

class UploadPlotsForm(Form):
    Plots_File = FileField(label = '')
    Plots_File.widget.attrs.update({'class': 'file-upload'})
    
class UploadTrialsForm(Form):
    Trials_File = FileField(label = '')
    Trials_File.widget.attrs.update({'class': 'file-upload'})
