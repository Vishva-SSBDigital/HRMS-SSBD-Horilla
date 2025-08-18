# from django.core.exceptions import ValidationError
# from django.db import models
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _

# from employee.models import Employee
# from horilla.models import HorillaModel  # consistent with your other models
# from base.horilla_company_manager import HorillaCompanyManager


# class Deputation(HorillaModel):
#     """
#     Simple employee deputation record.
#     """

#     employee = models.ForeignKey(
#         Employee,
#         on_delete=models.PROTECT,
#         related_name="deputations",
#         verbose_name=_("Employee"),
#     )
#     designation = models.CharField(
#         max_length=150, verbose_name=_("Deputation Employee Designation")
#     )
#     original_branch = models.CharField(
#         max_length=150, verbose_name=_("Original Branch (Created)")
#     )
#     deputed_to = models.CharField(
#         max_length=150, verbose_name=_("Deputed To (Branch/Office)")
#     )
#     start_date = models.DateField(verbose_name=_("Start Date"))
#     end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
#     email = models.EmailField(verbose_name=_("Email ID"))
#     current_position = models.CharField(
#     max_length=150,
#     verbose_name=_("Current Position"),
#     blank=True,
#     null=True,
# )

#     # company scoping like your other models (via the FK chain employee -> company)
#     objects = HorillaCompanyManager("employee__company_id")

#     class Meta:
#         verbose_name = _("Deputation")
#         verbose_name_plural = _("Deputations")
#         ordering = ("-id",)
#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(end_date__isnull=True) | models.Q(end_date__gte=models.F("start_date")),
#                 name="end_date_on_or_after_start_date",
#             )
#         ]

#     def clean(self):
#         if self.end_date and self.end_date < self.start_date:
#             raise ValidationError({"end_date": _("End date cannot be before start date.")})

#     def __str__(self):
#         return f"{self.employee} → {self.deputed_to} ({self.start_date} - {self.end_date or 'ongoing'})"

#     # handy URLs for templates
#     def get_update_url(self):
#         return reverse("deputation-update", kwargs={"pk": self.pk})

#     def get_delete_url(self):
#         return reverse("deputation-delete", kwargs={"pk": self.pk})
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from employee.models import Employee
from horilla.models import HorillaModel
from base.horilla_company_manager import HorillaCompanyManager


class Deputation(HorillaModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="deputations",
        verbose_name=_("Employee"),
    )
    designation = models.CharField(max_length=150, verbose_name=_("Deputation Employee Designation"))
    original_branch = models.CharField(max_length=150, verbose_name=_("Original Branch (Created)"))
    deputed_to = models.CharField(max_length=150, verbose_name=_("Deputed To (Branch/Office)"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    email = models.EmailField(verbose_name=_("Email ID"))
    current_position = models.CharField(
        max_length=150, verbose_name=_("Current Position"), blank=True, null=True
    )

    # company scoping via employee -> company
    objects = HorillaCompanyManager("employee__company_id")

    class Meta:
        verbose_name = _("Deputation")
        verbose_name_plural = _("Deputations")
        ordering = ("-id",)
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__isnull=True) | models.Q(end_date__gte=models.F("start_date")),
                name="end_date_on_or_after_start_date",
            )
        ]

    def clean(self):
        # IMPORTANT: guard both dates; this prevents TypeError when start_date is None
        super().clean()
        sd = self.start_date
        ed = self.end_date
        if sd is not None and ed is not None and ed < sd:
            raise ValidationError({"end_date": _("End date cannot be before start date.")})

    # OPTIONAL: if HorillaModel requires company to be set, copy it from employee
    def save(self, *args, **kwargs):
        if hasattr(self, "company_id") and not self.company_id and self.employee_id:
            # only set if your HorillaModel has company_id and it's empty
            emp = getattr(self, "employee", None)
            if emp and hasattr(emp, "company_id"):
                self.company_id = emp.company_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} → {self.deputed_to} ({self.start_date} - {self.end_date or 'ongoing'})"

    def get_update_url(self):
        return reverse("deputation-update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("deputation-delete", kwargs={"pk": self.pk})
