from django.db import models

class Trials(models.Model):
    plot_choices = (("Yield", "Yield"),
                    ("HR", "Headrows"),
                    ("SP", "Single Plant"),
                    ("Pot", "Pot"))

    trial_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Trial Id")
    plot_type = models.CharField(max_length = 10, choices = plot_choices, verbose_name = "Plot Type") 

    def __str__(self):
        return self.trial_id

#These should be cuts for HRs, nurs at loc for yield plots..
#Aka, can be whole trial of sub trial
#Not deleted, by view filters by default.
class Experiments(models.Model):
    status_choices = (("Planned", "Planned"),
                      ("Mapped", "Mapped"),
                      ("Packed", "Packed"),
                      ("Planted", "Planted"),
                      ("Failed", "Failed"),
                      ("Bags Made", "Bags Made"),
                      ("Harvested", "Harvested"))

    experiment_id = models.CharField(max_length=100, primary_key = True, verbose_name = "Experiment Id")
    trial = models.ForeignKey(Trials, on_delete = models.PROTECT, verbose_name = "Trial")
    status_text = models.CharField(max_length = 10, choices = status_choices, default = "Planned", verbose_name = "Packing Status")

    def save(self, *args, **kwargs):
        try:
            old_status = Experiments.objects.get(pk = self.experiment_id)
        except:
            old_status = None

        super().save(*args, **kwargs)

        if self.status != old_status:
            if (self.status == "Planted") & (old_status in ["Planned", "Mapped"]):
                Plots.objects.filter(Experiment = self.experiment_id).update(entry_fixed = True)


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
    location_text = models.CharField(max_length=200, verbose_name = "Location")
    amount_decimal = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0, verbose_name = "Seed Amount")
    amount_units = models.CharField(max_length = 3, choices = unit_choices, verbose_name = "Seed Units")
    entry_fixed = models.BooleanField(default = False, verbose_name = "Stock Fixed")

    def save(self, *args, **kwargs):
        if not self.entry_fixed:
            if self.amount_decimal > 0:
                self.entry_fixed = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.stock_id

#Defining foreignkey field with string makes field a "lazy" relationship and avoids circular dependency
class Plots(models.Model):
    plot_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Plot Id")
    source_stock = models.ForeignKey("Stocks", on_delete = models.PROTECT,null = True, blank = True, verbose_name = "Source Stock")
    family = models.ForeignKey('crossing.Families', on_delete = models.PROTECT, verbose_name = "Family")
    trial = models.ForeignKey(Trials, on_delete = models.PROTECT, verbose_name = "Trial")
    experiment = models.ForeignKey(Experiments, on_delete = models.PROTECT, verbose_name = "Experiment")
    desig_text = models.CharField(max_length=100, verbose_name = "Desig")
    gen_derived_int = models.PositiveIntegerField(verbose_name = "Derived Gen")
    gen_inbred_int = models.PositiveIntegerField(verbose_name = "Inbred Gen")
    entry_fixed = models.BooleanField(default = False, verbose_name = "Plot Fixed")

    def __str__(self):
        return self.plot_id


