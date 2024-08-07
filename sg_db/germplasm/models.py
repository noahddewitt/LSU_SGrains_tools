from django.db import models

#I previosly had two separate models for trials and experiments,
#Where experiments were a sub-field. I think that that's over-thinking it.
#Different HR cuts can just be different trials...
class Trials(models.Model):
    plot_choices = (("Yield", "Yield"),
                    ("HR", "Headrows"),
                    ("SP", "Single Plants"),
                    ("Pot", "Pots"))

    status_choices = (("Planned", "Planned"),
                      ("Mapped", "Mapped"),
                      ("Packed", "Packed"),
                      ("Planted", "Planted"),
                      ("Failed", "Failed"),
                      ("Bags Made", "Bags Made"),
                      ("Harvested", "Harvested"))

    trial_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Trial Id")
    year_text = models.CharField(max_length=4, verbose_name = "Year")
    location_text = models.CharField(max_length=3, verbose_name = "Location")
    plot_type = models.CharField(max_length = 10, choices = plot_choices, verbose_name = "Plot Type") 
    planting_date = models.DateField(null = True, blank = True, verbose_name = "Planting Date")
    harvest_date = models.DateField(null = True, blank = True, verbose_name = "Harvest Date")
    notes_text = models.CharField(max_length = 1000, null = True, blank = True, verbose_name = "Notes")
    status_text = models.CharField(max_length = 10, choices = status_choices, default = "Planned", verbose_name = "Packing Status")


    def save(self, *args, **kwargs):
        try:
            old_status = Trials.objects.get(pk = self.experiment_id).status_text
        except:
            old_status = None

        super().save(*args, **kwargs)

        if self.status_text != old_status:
            if (self.status_text == "Planted") & (old_status in ["Planned", "Mapped"]):
                Plots.objects.filter(Trial = self.experiment_id).update(entry_fixed = True)
    def __str__(self):
        return self.trial_id


#Defining foreignkey field with string makes field a "lazy" relationship and avoids circular dependency
#Both stocks and plots need generation columns because a single seed stock can be a bag of heads.
#Inbred generation advances on harvest of plot, derived generation advances on division of seed stock for plots or division of plots for seed stock...
class Stocks(models.Model):
    unit_choices = (("sds", "Seeds"),
                    ("hds", "Heads"),
                    ("g", "Grams"),
                    ("lb", "Pounds"))

    stock_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Stock Id")
    source_plot = models.ForeignKey("Plots", on_delete = models.PROTECT, null = True, blank = True, verbose_name = "Source Plot")
    family = models.ForeignKey('crossing.Families', on_delete = models.PROTECT, verbose_name = "Family")
    gen_derived_int = models.PositiveIntegerField(verbose_name = "Derived Gen")
    gen_inbred_int = models.PositiveIntegerField(verbose_name = "Inbred Gen")
    location_text = models.CharField(max_length=200, null = True, blank = True, verbose_name = "Location")
    amount_decimal = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0, verbose_name = "Seed Amount")
    amount_units = models.CharField(max_length = 3, choices = unit_choices, verbose_name = "Seed Units")
    entry_fixed = models.BooleanField(default = False, verbose_name = "Stock Fixed")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.stock_id

#Defining foreignkey field with string makes field a "lazy" relationship and avoids circular dependency
class Plots(models.Model):
    plot_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Plot Id")
    source_stock = models.ForeignKey("Stocks", on_delete = models.PROTECT,null = True, blank = True, verbose_name = "Source Stock")
    family = models.ForeignKey('crossing.Families', on_delete = models.PROTECT, null = True, blank = True, verbose_name = "Family")
    trial = models.ForeignKey(Trials, on_delete = models.PROTECT, verbose_name = "Trial")
    desig_text = models.CharField(max_length=100, verbose_name = "Desig")
    gen_derived_int = models.PositiveIntegerField(verbose_name = "Derived Gen", null = True, blank = True)
    gen_inbred_int = models.PositiveIntegerField(verbose_name = "Inbred Gen", null = True, blank = True)
    notes_text = models.CharField(max_length = 500, null = True, blank = True, verbose_name = "Notes")
    entry_fixed = models.BooleanField(default = False, verbose_name = "Plot Fixed")

    def __str__(self):
        return self.plot_id


