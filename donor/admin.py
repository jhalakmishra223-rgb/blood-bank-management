from django.contrib import admin
from .models import Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "blood_group",
        "phone",
        "city",
        "state",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "blood_group",
        "city",
    )

    list_filter = (
        "blood_group",
        "city",
        "state",
    )