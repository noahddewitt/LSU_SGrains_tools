from django.db import models
from django.utils import timezone

# Create your models here.
#Do we want to define a Desig class here and say:
#For Noah's DB, we just want to consider LSU lines, so only things
#Going into the WCP are desigs....

#I dont' think so. I think we want to load in a DESIG db from breedbase....


#Note that this will eventuall relate back to some Desig genotype db
class WCP_Entries(models.Model):
    wcp_id = models.CharField(max_length = 20, primary_key = True)
    year_text = models.CharField(max_length=4)
    eno_text = models.CharField(max_length=20)
    desig_text = models.CharField(max_length=200)
    purdy_text = models.CharField(max_length=500)
    cp_group_text = models.CharField(max_length=200)
    genes_text = models.CharField(max_length=500, blank = True)
    notes_text = models.CharField(max_length=1000, blank = True)
    sample_id_text = models.CharField(max_length=200, blank = True)

    def __str__(self):
        return self.desig_text

class Crosses(models.Model):
    cross_id = models.CharField(max_length=200, primary_key = True)
    parent_one = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_one')
    parent_two = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_two')
    cross_date = models.DateTimeField("Date Cross Made")
    crosser_text = models.CharField(max_length = 10)
    status_text = models.CharField(max_length = 10, default = "Made")
    seed_int = models.IntegerField(default = 0)

    def __str__(self):
        return self.cross_id

    def was_made_this_year(self):
        #Replace with nursery year
        return self.cross_date.year == timezone.now().year


class Families(models.Model):
    family_text = models.CharField(max_length=200, primary_key = True)
    cross_text = models.ForeignKey(Crosses, on_delete = models.PROTECT, related_name = 'cross')

    def __str__(self):
        return self.cross_text

