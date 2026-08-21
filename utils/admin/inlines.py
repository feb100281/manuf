from unfold.admin import TabularInline
from ..models import PipelineJob

class PipelineJobInline(TabularInline):
    model = PipelineJob
    
    extra = 0
    show_count = True

    ordering_field = "order"
    hide_ordering_field = True

    fields = [
        "order",
        "job",
        "enabled",
    ]

    autocomplete_fields = [
        "job",
    ]