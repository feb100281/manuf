from django.db import models
from .rentpremisses import RentPremis
from la.models import SA

class PremisContacts(models.Model):
    
    id = models.IntegerField(
            primary_key=True,
            verbose_name="ID",
        )
    rentpremis = models.ForeignKey(
            RentPremis,
            on_delete=models.DO_NOTHING,
            related_name="premises",
            verbose_name="Помещение",
        )
    
    sa = models.ForeignKey(
            SA,
            on_delete=models.DO_NOTHING,
            related_name="pc_sa",
            verbose_name="Документ",
        )
    
    class Meta:
            verbose_name = "Назначение помещений"
            verbose_name_plural = "Назначения помещений"            
    
    def __str__(self):
        return self.name or str(self.id)
    
    
    