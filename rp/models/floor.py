from django.db import models
from .property import Property

class Floor(models.Model):
    id = models.IntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.DO_NOTHING,
        related_name="floors",
        verbose_name="Объект недвижимости",
    )
    floor_number = models.IntegerField(
        verbose_name="Этаж",
    )
    area = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Площадь",
    )
    name_techplan = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Наименование по техплану",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
    )

    class Meta:
        verbose_name = "Этаж"
        verbose_name_plural = "Этажи"
        ordering = ["property", "floor_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["property", "floor_number"],
                name="uq_floor_property_number",
            )
        ]

    def __str__(self):
        return f"{self.property} — этаж {self.floor_number}"