from django.contrib import admin
from .table_sections import SASection
from .filters import HasFileFilter

from unfold.admin import ModelAdmin


from ..models import LA


@admin.register(LA)
class LAAdmin(ModelAdmin):

    list_display = [
        "number",
        "cp",
        "date_from",
    ]

    list_sections = [
        SASection,
    ]

    list_per_page = 25

    search_fields = [
        "number",
        "cp__name",
        "cp__inn",
    ]

    list_filter = [
        "date_from",        
    ]
    list_per_page = 25

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("cp")
            .prefetch_related("agreements")
        )
