from django.forms import Form, FileField

from .models import Stocks

class UploadStocksForm(Form):
    Stocks_File = FileField(label = '')
    Stocks_File.widget.attrs.update({'class': 'file-upload'})
