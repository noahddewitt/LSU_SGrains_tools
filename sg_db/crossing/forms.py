from django.forms import IntegerField, FileField, Form, ModelForm, NumberInput

from .models import WCP_Entries, Crosses

class WCPEntryForm(ModelForm):
    class Meta:
        model = WCP_Entries
        fields = ["wcp_id", "year_text", "eno_text", "desig_text", "purdy_text",
                  "cp_group_text", "genes_text", "notes_text", "sample_id_text"]

class UploadWCPForm(Form):
    WCP_Entries_File = FileField()


class CrossesEntryForm(ModelForm):
    class Meta:
        model = Crosses 
        fields = ["cross_id", "parent_one", "parent_two", "cross_date", 
                  "crosser_text", "status_text", "seed_int"]

class UploadCrossesForm(Form):
    Crosses_File = FileField(label = '')

    #Allows for modifying field attributes
    def __init__(self, *args, **kwargs):
        super(UploadCrossesForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'file-upload'

class UploadLabelsForm(Form):
    Labels_File = FileField()

class TimesToPrintForm(Form):
    Times_To_Print = IntegerField(label = 'Entry List Labels: ', initial = '1')
    Times_To_Print.widget.attrs.update({'style': 'width:5ch',
                                        'max': '99',
                                        'min': '1'})
