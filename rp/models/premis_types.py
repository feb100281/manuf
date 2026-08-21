from django.db import models

class PremisType(models.Model):
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
    icon = models.TextField(
        blank=True,
        null=True,
        verbose_name="SVG иконка",
    )
    icon_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Dash Iconify",
    )
    badge = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Badge",
    )

    class Meta:
        verbose_name = "Тип помещения"
        verbose_name_plural = "Типы помещений"

    def __str__(self):
        return self.name or str(self.id)

