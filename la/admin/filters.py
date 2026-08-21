from django.contrib import admin

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