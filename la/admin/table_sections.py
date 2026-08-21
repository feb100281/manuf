from django.urls import reverse
from django.utils.html import format_html

from unfold.sections import TableSection


class SASection(TableSection):
    verbose_name = "Документы"
    related_name = "agreements"

    fields = [
        "sa_type",
        "number_link",
        "date_from",
        "real_area",
        "calculated_area",
        "k_useful_area",
        "file",
    ]

    def number_link(self, instance):
        opts = instance._meta

        url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_change",
            args=[instance.pk],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            instance.number or instance.pk,
        )

    number_link.short_description = "Номер"

class LTection(TableSection):
    verbose_name = "Условия"    
    related_name = "sas"   
    fields = [
        "lttypes",
        "date_start",
        "date_finish",        
        "is_vat",
        "vat_rate",
        "la_value",        
    ]

