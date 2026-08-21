from django.db import models

class Company(models.Model):
    id = models.IntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    inn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="ИНН",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Наименование",
    )
    avatar = models.ImageField(
        upload_to="avatars/companies/",
        blank=True,
        null=True,
        verbose_name='Логотип'
    )

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name or str(self.id)


class BankAccount(models.Model):
    id = models.CharField(
        max_length=100,
        primary_key=True,
        verbose_name="ID",
    )
    owner = models.ForeignKey(
        Company,
        on_delete=models.DO_NOTHING,
        related_name="bank_accounts",
        verbose_name="Компания",
    )
    bb = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="ББ",
    )
    currency = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Валюта",
    )
    bank_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Банк",
    )
    bank_bic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="БИК",
    )
    
    avatar = models.ImageField(
            upload_to="avatars/companies/",
            blank=True,
            null=True,
            verbose_name='Логотип'
                )

    class Meta:
        verbose_name = "Банковский счет"
        verbose_name_plural = "Банковские счета"

    def __str__(self):
        return f"{self.bank_name or 'Банк'} — {self.id}"