from django.contrib import admin

# Register your models here.

from unfold.admin import ModelAdmin
from unfold.sections import TableSection
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    RelatedDropdownFilter
)

from .models import LA, SA, LTTypes, LT

from django.db.models import Q


class CPFilter(admin.SimpleListFilter):
    title = "Контрагент"
    parameter_name = "cp"

    template = "unfold/filters/text.html"

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        value = self.value()

        if not value:
            return queryset

        return queryset.filter(
            Q(la__cp__name__icontains=value)
            | Q(la__cp__inn__icontains=value)
        )

class HasFileFilter(admin.SimpleListFilter):
    title = "Файл"
    parameter_name = "has_file"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Есть файл"),
            ("no", "Нет файла"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(file="")

        if self.value() == "no":
            return queryset.filter(file="")

        return queryset

class SASection(TableSection):
    verbose_name = "Документы"

    # Это related_name из:
    # SA.la = ForeignKey(... related_name="agreements")
    related_name = "agreements"
    
    

    fields = [
        "sa_type",
        "number",
        "date_from",        
        "real_area",
        "calculated_area",
        "k_useful_area",
        "file"
    ]
    link_field = "number"

class LTection(TableSection):
    verbose_name = "Условия"

    # Это related_name из:
    # SA.la = ForeignKey(... related_name="agreements")
    related_name = "sas"
    
    

    fields = [
        "lttypes",
        "date_start",
        "date_finish",        
        "is_vat",
        "vat_rate",
        "la_value",
        
    ]
    


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
        CPFilter,
        HasFileFilter,
        "date_from",
    ]

    list_filter_submit = True

    list_select_related = (
        "la",
        "la__cp",
    )

    @admin.display(
        description="Контрагент",
        ordering="la__cp__name",
    )
    def cp(self, obj):
        return obj.la.cp

@admin.register(LTTypes)
class LTTypesAdmin(ModelAdmin):
    list_display = [
        "id",
        "name"
    ]

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

    
