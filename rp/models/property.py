from django.db import models
from corporate.models import Company

class Property(models.Model):
    id = models.IntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    owner = models.ForeignKey(
        Company,
        on_delete=models.DO_NOTHING,
        related_name="properties",
        verbose_name="Собственник",
    )
    kadast_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Кадастровый номер",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Наименование",
    )
    adress = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Адрес",
    )
    total_floors = models.IntegerField(
        default=0,
        verbose_name="Количество этажей",
    )
    total_area = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Общая площадь",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарии",
    )

    class Meta:
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"

    def __str__(self):
        return self.name or self.adress or str(self.id)

