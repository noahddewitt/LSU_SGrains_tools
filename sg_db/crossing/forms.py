from django.forms import IntegerField, FileField, Form, ModelForm, NumberInput

from .models import WCP_Entries, Crosses, Families


class WCPEntryForm(ModelForm):
    class Meta:
        model = WCP_Entries
        fields = ["wcp_id", "year_text", "eno_int", "desig_text", "purdy_text",
                  "cp_group_text", "source_text", "genes_text", "notes_text", "sample_id_text"]

class UploadWCPForm(Form):
    WCP_Entries_File = FileField(label = '')
    WCP_Entries_File.widget.attrs.update({'class': 'file-upload'})

class CrossesEntryForm(ModelForm):
    class Meta:
        model = Crosses 
        fields = ["cross_id", "year_text", "parent_one", "parent_two", "cross_date", 
                  "crosser_text", "status_text", "seed_int"]

class CrossesUpdateStatusForm(ModelForm):
    class Meta:
        model = Crosses 
        fields = ["status_text", "seed_int"]

class UploadCrossesForm(Form):
    Crosses_File = FileField(label = '')
    Crosses_File.widget.attrs.update({'class': 'file-upload'})

class FamiliesEntryForm(ModelForm):
    class Meta:
        model = Families 
        fields = ["family_id", "purdy_text", "genes_text", "notes_text", 'cross']

