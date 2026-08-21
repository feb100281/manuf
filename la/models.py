from django.db import models
from cp.models import CP

#Договора

class LA(models.Model):
    id = models.BigIntegerField(primary_key=True)

    cp = models.ForeignKey(
        CP,
        on_delete=models.DO_NOTHING,
        verbose_name="Контрагент",
    )

    number = models.CharField(
        max_length=100,
        verbose_name="Номер договора",
        blank=True,
        null=True,
    )

    date_from = models.DateField(
        verbose_name="Дата договора",
        blank=True,
        null=True,
    )

    date_signed = models.CharField(
        max_length=100,
        verbose_name="Дата подписания",
        blank=True,
        null=True,
    )

    date_expired = models.CharField(
        max_length=100,
        verbose_name="Срок действия",
        blank=True,
        null=True,
    )

    real_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Фактическая площадь",
        blank=True,
        null=True,
    )

    calculated_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Расчетная площадь",
        blank=True,
        null=True,
    )

    k_useful_area = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        verbose_name="Коэффициент полезной площади",
        blank=True,
        null=True,
    )

    comments = models.TextField(
        verbose_name="Комментарии",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Договор аренды"
        verbose_name_plural = "Договоры аренды"
        ordering = ["-date_from", "number"]

    def __str__(self):
        if self.number:
            return f"Договор №{self.number}"
        return f"Договор {self.pk}"

#Доп соглашения

class SA(models.Model):
    id = models.BigIntegerField(primary_key=True)

    la = models.ForeignKey(
        LA,
        on_delete=models.DO_NOTHING,
        related_name="agreements",
        verbose_name="Договор аренды",
    )
    
    sa_type = models.CharField(
        max_length=100,
        verbose_name='Тип документа',
        blank=True,
        null=True
    )

    number = models.CharField(
        max_length=100,
        verbose_name="Номер",
        blank=True,
        null=True,
    )

    date_from = models.DateField(
        verbose_name="Дата",
        blank=True,
        null=True,
    )

    date_signed = models.CharField(
        max_length=100,
        verbose_name="Дата подписания",
        blank=True,
        null=True,
    )

    date_expired = models.CharField(
        max_length=100,
        verbose_name="Срок действия",
        blank=True,
        null=True,
    )

    real_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Sфакт (м2)",
        blank=True,
        null=True,
    )

    calculated_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Sрасч (м2)",
        blank=True,
        null=True,
    )

    k_useful_area = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        verbose_name="Ks",
        blank=True,
        null=True,
    )

    comments = models.TextField(
        verbose_name="Комментарии",
        blank=True,
        null=True,
    )
    
    file = models.FileField(
        upload_to="la/",
        blank=True,
        null=True,
        verbose_name="Файл",
    )

    class Meta:
        verbose_name = "Документы"
        verbose_name_plural = "Документ"
        ordering = ["-date_from",]

    def __str__(self):
        if self.number:
            return f"{self.number}"
        return f"{self.pk}"

#Типы условий

class LTTypes(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name="Наименование условий",
        blank=True,
        null=True,
    )
    
    class Meta:
            verbose_name = "Тип условия"
            verbose_name_plural = "Типы условий"
            ordering = ["id",]
    
    def __str__(self):
            return f"{self.id} - {self.name}"

#Улсловия

class LT(models.Model):
    id = models.BigIntegerField(primary_key=True)
    sa = models.ForeignKey(
            SA,
            on_delete=models.DO_NOTHING,
            related_name="sas",
            verbose_name="Договор аренды",
            null=True,
            blank=True
        )
    lttypes = models.ForeignKey(
            LTTypes,
            on_delete=models.DO_NOTHING,
            related_name="la_type",
            verbose_name="Тип условий",
            null=True,
            blank=True
        )
    date_start = models.DateField(
            verbose_name="Дата начала",
            blank=True,
            null=True,
        )
    date_finish = models.DateField(
            verbose_name="Дата окончания",
            blank=True,
            null=True,
        )
    is_vat = models.BooleanField(
        verbose_name='В т.ч. НДС',
        blank=True,
        null=True,        
    )
    vat_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Ставка НДС",
        blank=True,
        null=True,
    )
    la_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Значение в договоре",
        blank=True,
        null=True,
    )
    pmt_terms = models.CharField(
        max_length=255,
        verbose_name='Условия оплаты',
        blank=True,
        null=True
    )
    term_description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    
    class Meta:
                verbose_name = "Условие"
                verbose_name_plural = "Условия"
                ordering = ["date_start",]
        
    def __str__(self):
            return f"{self.lttypes}"
    
    
    
    
    
    
  

