from django.contrib import admin
from .table_sections import LTection
from .inlines import LTInline
from .filters import HasFileFilter

from unfold.admin import ModelAdmin


from ..models import SA


@admin.register(SA)
class SAAdmin(ModelAdmin):

    list_display = [
        "sa_type",
        "cp",
        "number",
        "la",
        "date_from",
        "real_area",
        "calculated_area",
    ]

    search_fields = [
        "number",
        "la__number",
        "la__cp__name",
        "la__cp__inn",
    ]

    list_filter = [
        HasFileFilter,
        "date_from",
        "la__cp__name"
    ]

    list_filter_submit = True
    
    list_sections = [
            LTection,
        ]

    list_select_related = (
        "la",
        "la__cp",
    )
    
    inlines = [LTInline,]
    
    list_per_page = 25

    @admin.display(
        description="Контрагент",
        ordering="la__cp__name",
    )
    def cp(self, obj):
        return obj.la.cp
