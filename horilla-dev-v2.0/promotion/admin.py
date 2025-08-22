from django.contrib import admin
from django.contrib import admin
from .models import Promotion, LeaveEntitlement, SalaryBand

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("employee", "current_designation", "proposed_designation", "effective_from", "applied")
    list_filter = ("applied", "proposed_designation")
    search_fields = ("employee__employee_id", "employee__name")

@admin.register(LeaveEntitlement)
class LeaveEntitlementAdmin(admin.ModelAdmin):
    list_display = ("designation", "cl_per_year", "pl_per_year", "sl_per_year")

@admin.register(SalaryBand)
class SalaryBandAdmin(admin.ModelAdmin):
    list_display = ("designation", "default_basic")

# Register your models here.
