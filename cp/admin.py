from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminImageFieldWidget



from .models import CPType, CP


@admin.register(CPType)
class CPTypeAdmin(ModelAdmin):
    list_display = (       
        "name_with_icon",        
    )

    # search_fields = ("name",)
    ordering = ("id",)

   
    
    # @admin.display(description="Наименование", ordering="name")
    # def name_with_icon(self, obj):
    #     if not obj.icon:
    #         return obj.name

    #     return format_html(
    #         """
    #         <div style="
    #             display:flex;
    #             align-items:center;
    #             gap:10px;
    #         ">
    #             {}
    #             <span>{}</span>
    #         </div>
    #         """,
    #         mark_safe(obj.icon),
    #         obj.name,
    #     )

@admin.register(CP)
class CPAdmin(ModelAdmin):
    list_display = (
        "inn",
        "name",
        "avatar_display",
        "cptype",
        "email",
        "ogrn",
        "phone",
        "address",
        "cp_work",
        "avatar"
    )

    # search_fields = ("name",)
    ordering = ("name",)
    
    formfield_overrides = {

        models.ImageField: {

            "widget": UnfoldAdminImageFieldWidget,

        },

    }

    @admin.display(description="Аватар")
    def avatar_display(self, obj):
        if not obj.avatar:
            return "—"

        return format_html(
            """
            <img
                src="{}"
                class="h-10 w-10 rounded-full object-cover border border-base-200"
            >
            """,
            obj.avatar.url,
        )
