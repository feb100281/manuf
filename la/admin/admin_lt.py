from django.contrib import admin

from unfold.admin import ModelAdmin


from ..models import LT

@admin.register(LT)
class LTTAdmin(ModelAdmin):
    list_display = [
        "id",
        "sa",
        "lttypes",
        "date_start",
        "date_finish",
        "is_vat",
        "vat_rate",
        "la_value",
        "pmt_terms",
        # "term_description"
    ]
    list_per_page = 25