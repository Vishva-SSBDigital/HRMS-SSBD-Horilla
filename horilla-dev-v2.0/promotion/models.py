# from django.db import models
# from django.conf import settings
# from django.utils import timezone

# # ---- Reference models you likely already have ----
# # If you already have these in another app, import those and delete these placeholders.

# class Designation(models.Model):
#     """Existing master: e.g., Clerk, Officer, Manager, etc."""
#     name = models.CharField(max_length=120, unique=True)

#     # Optional: link to a grade code if you use it
#     grade_code = models.CharField(max_length=20, blank=True, null=True)

#     def __str__(self):
#         return self.name


# class Employee(models.Model):
#     """Existing employee master."""
#     EMP_STATUS = (
#         ('REGULAR', 'Regular'),
#         ('CONTRACT', 'Contractual'),
#     )
#     employee_id = models.CharField(max_length=30, unique=True, db_index=True)
#     name = models.CharField(max_length=200)
#     status = models.CharField(max_length=10, choices=EMP_STATUS, default='REGULAR')
#     designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='employees')
#     date_joined = models.DateField(default=timezone.now)

#     def __str__(self):
#         return f"{self.employee_id} - {self.name}"


# # ---- Leave & Pay masters ----

# class LeaveEntitlement(models.Model):
#     """
#     Annual entitlement for a designation/grade.
#     These are the *caps* used to auto-calc 'Adjusted Leave Position Post Promotion'.
#     """
#     designation = models.OneToOneField(Designation, on_delete=models.CASCADE, related_name='leave_entitlement')
#     cl_per_year = models.PositiveIntegerField(default=0)  # Casual Leave
#     pl_per_year = models.PositiveIntegerField(default=0)  # Privilege Leave
#     sl_per_year = models.PositiveIntegerField(default=0)  # Sick Leave

#     def __str__(self):
#         return f"Entitlement for {self.designation.name}"


# class SalaryBand(models.Model):
#     """
#     Default/basic pay attached to a designation (simple version).
#     If you have full pay-scales, replace with your structure.
#     """
#     designation = models.OneToOneField(Designation, on_delete=models.CASCADE, related_name='salary_band')
#     default_basic = models.DecimalField(max_digits=12, decimal_places=2)

#     def __str__(self):
#         return f"SalaryBand for {self.designation.name}"


# class LeaveBalance(models.Model):
#     """
#     Per-employee current leave balance. If you already have this, reuse it.
#     """
#     employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='leave_balance')
#     cl_balance = models.PositiveIntegerField(default=0)
#     pl_balance = models.PositiveIntegerField(default=0)
#     sl_balance = models.PositiveIntegerField(default=0)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"LeaveBalance({self.employee.employee_id})"


# # ---- Promotion transaction ----

# class Promotion(models.Model):
#     """
#     Stores the promotion proposal and the applied changes.
#     """
#     EMP_STATUS = Employee.EMP_STATUS

#     employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='promotions')

#     current_status = models.CharField(max_length=10, choices=EMP_STATUS)
#     proposed_status = models.CharField(max_length=10, choices=EMP_STATUS)

#     current_designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='promotions_from')
#     proposed_designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='promotions_to')

#     # Leave before and adjusted (snapshot)
#     current_cl = models.PositiveIntegerField(default=0)
#     current_pl = models.PositiveIntegerField(default=0)
#     current_sl = models.PositiveIntegerField(default=0)

#     adjusted_cl = models.PositiveIntegerField(default=0)
#     adjusted_pl = models.PositiveIntegerField(default=0)
#     adjusted_sl = models.PositiveIntegerField(default=0)

#     # Salary proposal (basic)
#     proposed_basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     effective_from = models.DateField()

#     # Book-keeping
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='promotions_created'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     applied = models.BooleanField(default=False)  # set True after commit changes

#     def __str__(self):
#         return f"Promotion({self.employee.employee_id} → {self.proposed_designation.name} on {self.effective_from})"

# # Create your models here.


# promotion/models.py
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# -----------------------------
# Master: Designation / Grade
# -----------------------------
class Designation(models.Model):
    """E.g., Clerk, Officer, Manager, etc."""
    name = models.CharField(max_length=120, unique=True, db_index=True)
    grade_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("Designation")
        verbose_name_plural = _("Designations")

    def __str__(self) -> str:
        return self.name


# -----------------------------
# Leave & Pay masters
# -----------------------------
class LeaveEntitlement(models.Model):
    """
    Annual entitlement by designation/grade.
    Used to clamp 'Adjusted Leave Position Post Promotion'.
    """
    designation = models.OneToOneField(
        Designation,
        on_delete=models.CASCADE,
        related_name="leave_entitlement",
    )
    cl_per_year = models.PositiveIntegerField(default=0)  # Casual Leave
    pl_per_year = models.PositiveIntegerField(default=0)  # Privilege Leave
    sl_per_year = models.PositiveIntegerField(default=0)  # Sick Leave

    class Meta:
        verbose_name = _("Leave Entitlement")
        verbose_name_plural = _("Leave Entitlements")

    def __str__(self) -> str:
        return f"Entitlement for {self.designation.name}"


class SalaryBand(models.Model):
    """
    Default/basic pay attached to a designation.
    Replace with full pay-scale tables if you have them.
    """
    designation = models.OneToOneField(
        Designation,
        on_delete=models.CASCADE,
        related_name="salary_band",
    )
    default_basic = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        verbose_name = _("Salary Band")
        verbose_name_plural = _("Salary Bands")

    def __str__(self) -> str:
        return f"SalaryBand for {self.designation.name}"


# -----------------------------
# Per-employee snapshot objects
# -----------------------------
class LeaveBalance(models.Model):
    """
    Per-employee current leave balance.
    NOTE: This references the real Employee model from the `employee` app.
    """
    employee = models.OneToOneField(
        "employee.Employee",
        on_delete=models.CASCADE,
        related_name="leave_balance",
    )
    cl_balance = models.PositiveIntegerField(default=0)
    pl_balance = models.PositiveIntegerField(default=0)
    sl_balance = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Leave Balance")
        verbose_name_plural = _("Leave Balances")

    def __str__(self) -> str:
        # Guard against missing employee_id property on your Employee model
        emp_code = getattr(self.employee, "employee_id", str(self.employee_id))
        return f"LeaveBalance({emp_code})"


# -----------------------------
# Promotion transaction
# -----------------------------
class EmpStatus(models.TextChoices):
    REGULAR = "REGULAR", _("Regular")
    CONTRACT = "CONTRACT", _("Contractual")


class Promotion(models.Model):
    """
    Stores the promotion proposal and the applied changes.
    """
    employee = models.ForeignKey(
        "employee.Employee",
        on_delete=models.PROTECT,
        related_name="promotions",
        db_index=True,
    )

    # Current snapshot (at creation time) and proposed target
    current_status = models.CharField(max_length=10, choices=EmpStatus.choices)
    proposed_status = models.CharField(max_length=10, choices=EmpStatus.choices)

    current_designation = models.ForeignKey(
        Designation,
        on_delete=models.PROTECT,
        related_name="promotions_from",
    )
    proposed_designation = models.ForeignKey(
        Designation,
        on_delete=models.PROTECT,
        related_name="promotions_to",
    )

    # Leave snapshot (before) and adjusted (post-promotion caps)
    current_cl = models.PositiveIntegerField(default=0)
    current_pl = models.PositiveIntegerField(default=0)
    current_sl = models.PositiveIntegerField(default=0)

    adjusted_cl = models.PositiveIntegerField(default=0)
    adjusted_pl = models.PositiveIntegerField(default=0)
    adjusted_sl = models.PositiveIntegerField(default=0)

    # Salary proposal (basic)
    proposed_basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    effective_from = models.DateField()

    # Book-keeping
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="promotions_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    applied = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=["employee", "effective_from"]),
            models.Index(fields=["applied", "created_at"]),
        ]
        verbose_name = _("Promotion")
        verbose_name_plural = _("Promotions")

    def __str__(self) -> str:
        emp_code = getattr(self.employee, "employee_id", str(self.employee_id))
        return f"Promotion({emp_code} → {self.proposed_designation.name} on {self.effective_from})"

    # Optional helpers
    @property
    def is_pending(self) -> bool:
        return not self.applied

    @property
    def is_applied(self) -> bool:
        return self.applied
