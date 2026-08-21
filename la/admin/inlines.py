from unfold.admin import TabularInline
from ..models import LT

class LTInline(TabularInline):

    model = LT
    fields = [
        "lttypes",
        "date_start",
        "date_finish",
        "la_value",
        "is_vat",
        "vat_rate",
        "pmt_terms",
    ]
    readonly_fields = fields
    extra = 0
    tab = True
    show_change_link = True
    show_count = True
