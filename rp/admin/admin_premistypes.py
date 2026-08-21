from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..models.premis_types import PremisType


@admin.register(PremisType)
class PremisTypeAdmin(ModelAdmin):

    list_display = [
        "name_with_icon",
        "icon_name",
        "badge",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "id",
                    "name",
                    "badge",
                ],
            },
        ),
        (
            "Иконка",
            {
                "classes": ["tab"],
                "fields": [
                    "icon",
                    "icon_name",
                ],
            },
        ),
    )

    @admin.display(description="Наименование", ordering="name")
    def name_with_icon(self, obj):
        if not obj.icon:
            return obj.name

        return format_html(
            """
            <div style="
                display:flex;
                align-items:center;
                gap:10px;
            ">
                {}
                <span>{}</span>
            </div>
            """,
            mark_safe(obj.icon),
            obj.name,
        )

    
