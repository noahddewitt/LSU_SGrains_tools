import re

from datetime import date, timedelta

from django.db import models
from django.utils import timezone

from germplasm.models import Stocks

class CurrentYearManager(models.Manager):
    #We often begin the crossing year in november or december the year prior. 
    #So add some days to make sure we stay in the same

    def get_queryset(self):
        crossingYear_adjustedDate = date.today() + timedelta(60)
        crossingYear = str(crossingYear_adjustedDate.year)
        return super().get_queryset().filter(year_text=crossingYear) #crossingYear)

class WCP_Entries(models.Model):
    wcp_id = models.CharField(max_length = 20, primary_key = True, verbose_name = "WCP Id")
    year_text = models.CharField(max_length=4, verbose_name = "Year")
    eno_int = models.IntegerField(verbose_name = "Eno")
    desig_text = models.CharField(max_length=200, verbose_name = "Desig")
    purdy_text = models.CharField(max_length=500, blank = True, verbose_name = "Purdy Pedigree")
    cp_group_text = models.CharField(max_length=200, verbose_name = "Group")
    source_text = models.CharField(max_length=50, blank = True, verbose_name = "Source")
    genes_text = models.CharField(max_length=500, blank = True, verbose_name = "Genes")
    notes_text = models.CharField(max_length=1000, blank = True, verbose_name = "Notes")
    sample_id_text = models.CharField(max_length=200, blank = True, verbose_name = "Geno Id")

    objects = models.Manager()
    cur_year_objects = CurrentYearManager() 

    def __str__(self):
        return self.desig_text

class Crosses(models.Model):
    status_choices = (("Set", "Set"),
                      ("Made", "Made"),
                      ("Failed", "Failed"))

    cross_id = models.CharField(max_length=200, primary_key = True, verbose_name = "Cross Id")
    year_text = models.CharField(max_length=4, verbose_name = "Year")
    parent_one = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_one', verbose_name = "Parent One")
    parent_two = models.ForeignKey(WCP_Entries, on_delete = models.PROTECT,related_name = 'parent_two', verbose_name = "Parent Two")
    cross_date = models.DateTimeField(verbose_name = "Crossing Date", blank = True, null = True)
    crosser_text = models.CharField(max_length = 10, verbose_name = "Crosser", blank = True, null = True)
    status_text = models.CharField(max_length = 10, default = "Made", choices = status_choices, verbose_name = "Status")
    seed_int = models.IntegerField(default = 0, verbose_name = "Seed")

    def save(self, *args, **kwargs):
        try:
            old_status = Crosses.objects.get(pk = self.cross_id).status_text
        except:
            old_status = None

        super().save(*args, **kwargs)

        #Allow historic data without creating new families
        if int(self.year_text) < date.today().year:
            create_family = False
        else:
            create_family = True

        print(create_family)
        if self.status_text == "Set" and old_status != "Set" and create_family == True:
            self.create_families()


    def create_families(self):
        newPurdyText = self.parent_one.desig_text + " / " + self.parent_two.desig_text

        print(newPurdyText)

        #Fix this by defining custom function below
        newGenes = Crosses.create_gene_str(self.parent_one.genes_text, self.parent_two.genes_text)

        print(newGenes)

        #Returns tuple
        objects, created = Families.objects.update_or_create(
                year_text = self.year_text,
                purdy_text = newPurdyText,
                genes_text = newGenes,
                cross = self)

    def create_gene_str(gene_str_one, gene_str_two):
        #Turn in to dics to allow matching and use of hets
        gene_dict_one = Crosses.gene_str_to_dict(gene_str_one) 
        gene_dict_two = Crosses.gene_str_to_dict(gene_str_two) 

        #Sets don't preserve order. A little hacky.
        search_genes = ["FHB1", "FHB_JT", "H13", "H13B", "BYDV2"]
        search_genes.extend(list(set(gene_dict_one.keys()) - set(search_genes)))
        search_genes.extend(list(set(gene_dict_two.keys()) - set(search_genes)))
        new_gene_str = ""
    
        #This is a pretty ugly stretch.
        for gene in search_genes:
            gene_one = gene_dict_one.get(gene) or ""
            gene_two = gene_dict_two.get(gene) or ""

            #Move on if neither parent has some form of gene
            if {gene_one, gene_two} != {''}:
                if gene_one != '':
                    gene_one_match = re.search("(HET.*)", gene_one.upper())
                    if gene_one_match is None:
                        gene_class_one = "HOM"
                    else:
                        gene_class_one = gene_one_match.group(1)
                else:
                    gene_class_one = ''
                
                if gene_two != '':
                    gene_two_match = re.search("(HET.*)", gene_two.upper())
                    if gene_two_match is None:
                        gene_class_two = "HOM"
                    else:
                        gene_class_two = gene_two_match.group(1)
                else:
                    gene_class_two = ''

                gene_class_set = {gene_class_one, gene_class_two}

                #Both parents homozygous
                if gene_class_set == {'HOM'}:
                    new_gene = gene
                elif (gene_class_set == {'', 'HOM'} or gene_class_set == {'HET'}):
                    new_gene = gene + "Het" 
                #These classes convey uncertainty. You can't go from uncertain to certain.
                elif (gene_class_set == {'HOM', 'HET'} or gene_class_set == {'HOM', 'HET+'} or
                     gene_class_set == {'HOM', 'HET-'} or gene_class_set == {'HET', 'HET+'}):
                    new_gene = gene + "Het+"
                elif (gene_class_set == {'', 'HET'} or gene_class_set == {'HET', 'HET-'} or 
                     gene_class_set == {'', 'HET+'} or gene_class_set == {'', 'HET-'}):
                    new_gene = gene + "Het-"
                else:
                    #This won't print in this context.
                    print("Classs " + str(gene_class_set) + " unrecognized.")
                    new_gene = "Error"
                
                if new_gene_str == "":
                    new_gene_str += new_gene
                else:
                    new_gene_str += ", " + new_gene

        return(new_gene_str) 

    def gene_str_to_dict(gene_str):
        gene_list = re.sub(" ", "", gene_str).split(",")
        gene_list_unique = [re.sub("[Hh][Ee][Tt]\+*\-*$", "", gene).upper() for gene in gene_list]

        gene_dict = {gene_list_unique[i]: gene_list[i] for i in range(len(gene_list))} 

        return(gene_dict)

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
            if not Families.cur_year_objects.all(): 
                self.order_int = 1
            else:
                self.order_int = Families.cur_year_objects.all().aggregate(models.Max('order_int'))['order_int__max'] + 1
            self.family_id = "LA" + self.year_text[2:4:1] + str(self.order_int).zfill(3)
        super(Families, self).save(*args, **kwargs) 
        
        self.create_f1_seed()

    def create_f1_seed(self):
        new_id = "S-" + self.cross.cross_id

        objects, created = Stocks.objects.update_or_create(
                stock_id = new_id,
                family = self,
                gen_derived_int = 0,
                gen_inbred_int = 1,
                location_text = "",
                amount_decimal = self.cross.seed_int,
                amount_units = "sds")

    def __str__(self):
        return self.family_id

