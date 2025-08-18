# from django.contrib import admin
# from .models import Deputation


# @admin.register(Deputation)
# class DeputationAdmin(admin.ModelAdmin):
#     list_display = ("employee", "designation", "original_branch", "deputed_to", "start_date", "end_date", "email", "current_position", "is_active")
#     list_filter = ("original_branch", "deputed_to", "designation", "is_active")
#     search_fields = ("employee__employee_first_name", "employee__employee_last_name", "email", "original_branch", "deputed_to", "current_position")


# # Register your models here.
from datetime import date
from django.contrib import admin
from .models import Deputation

@admin.register(Deputation)
class DeputationAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "designation",
        "original_branch",
        "deputed_to",
        "start_date",
        "end_date",
        "status_display",     # computed column
        "email",
        "current_position",
        "is_active",          # remove if your model doesn't have it
    )
    list_filter = (
        "original_branch",
        "deputed_to",
        "designation",
        ("start_date", admin.DateFieldListFilter),
        ("end_date", admin.DateFieldListFilter),
        "is_active",          # remove if not present
    )
    search_fields = (
        "employee__employee_first_name",
        "employee__employee_last_name",
        "email",
        "original_branch",
        "deputed_to",
        "current_position",
    )
    date_hierarchy = "start_date"
    ordering = ("-id",)
    list_per_page = 50

    # performance: avoid N+1 on the employee FK
    list_select_related = ("employee",)

    # nicer editing of the FK (ensure EmployeeAdmin has search_fields set)
    autocomplete_fields = ("employee",)

    def status_display(self, obj):
        if obj.end_date is None or obj.end_date >= date.today():
            return "Ongoing"
        return "Ended"
    status_display.short_description = "Status"
    status_display.admin_order_field = "end_date"
