from django.contrib import admin
from django.http import FileResponse, Http404,HttpResponse
# Register your models here.
# admin.py
from pathlib import Path

from django.db import models

from django_json_widget.widgets import JSONEditorWidget

from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import Jobs

from django.contrib.admin import register
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action



from unfold.admin import ModelAdmin, TabularInline
from .models import Pipeline, PipelineJob

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


@admin.register(Jobs)
class JobsAdmin(ModelAdmin):
       

    list_display = [
        "name",
        "jobtype",
        "scope",
        "status",
        "lastrun",
    ]

    list_filter = [
        "jobtype",
        "scope",
        "status",
    ]

    search_fields = [
        "name",
        "command",
        "description",
    ]

    ordering = [
        "jobtype",
        "name",
    ]
    
    readonly_fields = [
    "status",
    "lastrun",
    ]

    list_filter_sheet = False
    list_fullwidth = True
    warn_unsaved_form = True
    change_form_show_cancel_button = True

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
        models.JSONField: {
            "widget": JSONEditorWidget,
        },
    }

    fieldsets = (
        (
            "Задача",
            {
                "fields": [
                    ("name", "jobtype"),
                    ("scope", "status"),
                    "description",
                ],
            },
        ),

        (
            "Выполнение",
            {
                "classes": ["tab"],
                "fields": [
                    "command",
                    "param",
                ],
            },
        ),

        (
            "Состояние",
            {
                "classes": ["tab"],
                "fields": [
                    "lastrun",
                    "logfile",
                ],
            },
        ),
    )
    

    actions_row = [
        "run_command",
        "open_log",
        
    ]

    @action(
        description="Открыть лог",
        permissions=["open_log"],
        url_path="open-log",
        attrs={"target": "_blank"},
        icon="description",
    )
    def open_log(self, request: HttpRequest, object_id: int):

        job = self.get_object(request, object_id)

        if not job or not job.logfile:
            raise Http404("Лог отсутствует")

        path = Path(job.logfile.path)

        if not path.exists():
            raise Http404("Файл лога не найден")

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        return HttpResponse(
            f"<pre>{text}</pre>",
            content_type="text/html; charset=utf-8",
        )

    def has_open_log_permission(self, request: HttpRequest):
        return True
    
    
    
@admin.register(PipelineJob)
class PipelineJobAdmin(ModelAdmin):
    pass
