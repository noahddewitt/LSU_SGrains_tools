from django.db import models

class Trials(models.Model):
    trial_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Trial Id")

    def __str__(self):
        return self.trial_id

#class Stocks(models.Model):
#    stock_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Stock Id")
#    source_plot = models.ForeignKey(Plots, on_delete = models.PROTECT, blank = True, verbose_name = "Source Plot")

 #   def __str__(self):
  #      return self.stock_id

#class Plots(models.Model):
 #   plot_id = models.CharField(max_length=40, primary_key = True, verbose_name = "Plot Id")
  #  source_stock = models.ForeignKey(Stocks, on_delete = models.PROTECT, blank = True, verbose_name = "Source Stock")
   # trial = models.ForeignKey(Trials, on_delete = models.PROTECT, verbose_name = "Trial")

    #def __str__(self):
    #    return self.plot_id
