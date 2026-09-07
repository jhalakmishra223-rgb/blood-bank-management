from django.contrib import admin
from .models import BloodInventory, BloodRequest
@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = (
        "blood_group",
        "units_available",
        "last_updated",
    )
    search_fields = ("blood_group",)
    ordering = ("blood_group",)
@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = (
        "patient_name",
        "blood_group",
        "units_required",
        "hospital_name",
        "city",
        "status",
        "requested_on",
    )
    list_filter = (
        "blood_group",
        "status",
        "city",
    )
    search_fields = (
        "patient_name",
        "hospital_name",
        "city",
    )
    ordering = ("-requested_on",)