from django.db import models
from django.utils import timezone

class CurrentYearManager(models.Manager):
    crossingYear = "2024" #Modify this as modification of datetime 
    def get_queryset(self):
        return super().get_queryset().filter(year_text="2024")

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

    objects = models.Manager()
    cur_year_objects = CurrentYearManager() 

    def __str__(self):
        return self.desig_text

class Crosses(models.Model):
    cross_id = models.CharField(max_length=200, primary_key = True, verbose_name = "Cross Id")
    year_text = models.CharField(max_length=4, verbose_name = "Year")
    parent_one = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_one', verbose_name = "Parent One")
    parent_two = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_two', verbose_name = "Parent Two")
    cross_date = models.DateTimeField(verbose_name = "Crossing Date")
    crosser_text = models.CharField(max_length = 10, verbose_name = "Crosser")
    status_text = models.CharField(max_length = 10, default = "Made", verbose_name = "Status")
    seed_int = models.IntegerField(default = 0, verbose_name = "Seed")

    #def save(self, *args, **kwargs):
    #    self.create_families()
    #    return super().save(*args, **kwargs)

    #def create_families(self):
    #    #Subset self by status?

    #    newPurdyText = self.parent_one.desig_text + " / " + self.parent_two.desig_text

        #Fix this
     #   newGenes = self.parent_one.genes_text

     #   ... = Families.objects.update_or_create(
     #           year_text = self.year_text,
     #           purdy_text = newPurdyText,
     #           genes_text = newGenes,
     #           cross = self.cross_id
      #          )

    def __str__(self):
        return self.cross_id


class Families(models.Model):
    family_id = models.CharField(max_length=200, primary_key = True, verbose_name = "Family", default = "placeholder")
    year_text = models.CharField(max_length=4, verbose_name = "Cross Year")
    order_int = models.IntegerField(verbose_name = "Cross Order", default = 0)
    purdy_text = models.CharField(max_length=500, verbose_name = "Purdy Pedigree")
    genes_text = models.CharField(max_length=500, blank = True, verbose_name = "Genes")
    notes_text = models.CharField(max_length=10000, blank = True, verbose_name = "Notes")
    cross = models.ForeignKey(Crosses, on_delete = models.PROTECT, related_name = 'cross', verbose_name = "Cross Id")

    objects = models.Manager()
    cur_year_objects = CurrentYearManager() 

    def save(self, *args, **kwargs):
        if self.family_id == "placeholder":
            self.order_int = Families.cur_year_objects.all().aggregate(models.Max('order_int'))['order_int__max'] + 1
            self.family_id = "LA" + self.year_text[2:4:1] + str(self.order_int).zfill(3)
        super(Families, self).save(*args, **kwargs) 

    def __str__(self):
        return self.family_id

