from django.contrib import admin

from .models import ChocoSoftware, InstalledSoftware, InstallomatorLabel


class ChocoAdmin(admin.ModelAdmin):
    readonly_fields = ("added",)


class InstallomatorAdmin(admin.ModelAdmin):
    readonly_fields = ("added", "updated")
    list_display = ("__str__", "version", "added")


admin.site.register(ChocoSoftware, ChocoAdmin)
admin.site.register(InstallomatorLabel, InstallomatorAdmin)
admin.site.register(InstalledSoftware)
