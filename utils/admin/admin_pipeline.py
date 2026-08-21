from django.contrib import admin

from django.db import models

from django_json_widget.widgets import JSONEditorWidget

from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget


from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .inlines import PipelineJobInline

from unfold.admin import ModelAdmin
from ..models import Pipeline

@admin.register(Pipeline)
class PipelineAdmin(ModelAdmin):

    inlines = [
        PipelineJobInline,
    ]

    list_display = [
        "name",
        "enabled",
    ]

    list_filter = [
        "enabled",
    ]

    search_fields = [
        "name",
        "description",
    ]

    fieldsets = (
        (
            "Pipeline",
            {
                "fields": [
                    ("name", "enabled"),
                    "description",
                ],
            },
        ),
    )
    
    formfield_overrides = {
            models.TextField: {
                "widget": WysiwygWidget,
            },
            models.JSONField: {
                "widget": JSONEditorWidget,
            },
        }