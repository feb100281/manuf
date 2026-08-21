from django.contrib import admin

from unfold.admin import ModelAdmin


from ..models import LTTypes

@admin.register(LTTypes)
class LTTypesAdmin(ModelAdmin):
    list_display = [        
        "name"
    ]