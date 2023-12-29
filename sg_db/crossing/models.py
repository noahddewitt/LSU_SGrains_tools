from django.db import models
from django.db.models.functions import Cast
from django.utils import timezone

#Do we want to define a Desig class here and say:
#For Noah's DB, we just want to consider LSU lines, so only things

class WCP_Entries(models.Model):
    wcp_id = models.CharField(max_length = 20, primary_key = True, verbose_name = "WCP Id")
    year_text = models.CharField(max_length=4, verbose_name = "Year")
    eno_text = models.CharField(max_length=20, verbose_name = "Eno")
    desig_text = models.CharField(max_length=200, verbose_name = "Desig")
    purdy_text = models.CharField(max_length=500, verbose_name = "Purdy Pedigree")
    cp_group_text = models.CharField(max_length=200, verbose_name = "Group")
    genes_text = models.CharField(max_length=500, blank = True, verbose_name = "Genes")
    notes_text = models.CharField(max_length=1000, blank = True, verbose_name = "Notes")
    sample_id_text = models.CharField(max_length=200, blank = True, verbose_name = "Genotyping Id")


    def __str__(self):
        return self.desig_text

class Crosses(models.Model):
    cross_id = models.CharField(max_length=200, primary_key = True, verbose_name = "Cross Id")
    parent_one = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_one', verbose_name = "Parent One")
    parent_two = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_two', verbose_name = "Parent Two")
    cross_date = models.DateTimeField(verbose_name = "Crossing Date")
    crosser_text = models.CharField(max_length = 10, verbose_name = "Crosser")
    status_text = models.CharField(max_length = 10, default = "Made", verbose_name = "Status")
    seed_int = models.IntegerField(default = 0, verbose_name = "Seed")

    def __str__(self):
        return self.cross_id

    def was_made_this_year(self):
        #Replace with nursery year
        return self.cross_date.year == timezone.now().year


class Families(models.Model):
    family_id = models.CharField(max_length=200, primary_key = True, verbose_name = "Family")
    purdy_text = models.CharField(max_length=500, verbose_name = "Purdy Pedigree")
    genes_text = models.CharField(max_length=500, verbose_name = "Genes")
    notes_text = models.CharField(max_length=10000, verbose_name = "Notes")
    cross_text = models.ForeignKey(Crosses, on_delete = models.PROTECT, related_name = 'cross', verbose_name = "Cross Id")

    def __str__(self):
        return self.cross_text

