from django.db import models
from .floor import Floor
from .premis_status import PremisStatus
from .premis_types import PremisType

class RentPremis(models.Model):
    id = models.IntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Наименование",
    )
    premistype = models.ForeignKey(
        PremisType,
        on_delete=models.DO_NOTHING,
        related_name="premises",
        verbose_name="Тип помещения",
    )
    floor = models.ForeignKey(
        Floor,
        on_delete=models.DO_NOTHING,
        related_name="premises",
        verbose_name="Этаж",
    )
    area = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Площадь",
    )
    characteristic = models.TextField(
        blank=True,
        null=True,
        verbose_name="Характеристика",
    )
    premisstatus = models.ForeignKey(
        PremisStatus,
        on_delete=models.DO_NOTHING,
        related_name="premises",
        verbose_name="Статус помещения",
    )

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        ordering = ["floor", "name"]

    def __str__(self):
        return self.name or str(self.id)