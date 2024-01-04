from django.forms import IntegerField, FileField, BooleanField, Form, ModelForm, NumberInput


class UploadLabelsForm(Form):
    Labels_File = FileField()
    Labels_File.widget.attrs.update({'class': 'file-upload'})

    Times_To_Print = IntegerField(label = 'Times to print', initial = '1')
    Times_To_Print.widget.attrs.update({'class': 'times-counter',
                                        'style': 'width:20ch',
                                        'max': '99',
                                        'min': '1'})

    Include_Barcode = BooleanField(label = "Include Barcode?", initial = True, required = False)

    #Date


#I believe this is only called by WCP_Entries view
class TimesToPrintForm(Form):
    Times_To_Print = IntegerField(label = 'Entry List Labels: ', initial = '1')
    Times_To_Print.widget.attrs.update({'style': 'width:5ch',
                                        'class': 'times-counter',
                                        'max': '99',
                                        'min': '1'})

