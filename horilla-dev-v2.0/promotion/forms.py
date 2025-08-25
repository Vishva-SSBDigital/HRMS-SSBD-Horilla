
# from django import forms
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
# from .models import Promotion, Designation
# from employee.models import Employee
# from base.models import Department


# class EmployeeChoiceField(forms.ModelChoiceField):
#     """Readable label: 'First Last — EMP001' with safe fallbacks."""
#     def label_from_instance(self, obj: Employee) -> str:
#         fn = getattr(obj, "employee_first_name", "") or getattr(obj, "first_name", "")
#         ln = getattr(obj, "employee_last_name", "") or getattr(obj, "last_name", "")
#         code = getattr(obj, "employee_id", "") or getattr(obj, "emp_code", "") or getattr(obj, "code", "")
#         name = (" ".join([x for x in [fn, ln] if x]).strip()
#                 or getattr(obj, "name", "")
#                 or str(obj.pk))
#         return f"{name} — {code}" if code else name


# class PromotionForm(forms.ModelForm):
#     # Employee dropdown (by NAME) — replaces any employee_id textbox
#     employee = EmployeeChoiceField(
#         queryset=Employee.objects.all().order_by("employee_first_name", "employee_last_name", "id"),
#         label=_("Employee"),
#         widget=forms.Select(attrs={"class": "oh-input oh-select", "id": "id_employee"}),
#         empty_label="---------",
#     )

#     # Optional helper (not saved to Promotion)
#     department = forms.ModelChoiceField(
#         queryset=Department.objects.none(),
#         label=_("Department"),
#         required=False,
#         widget=forms.Select(attrs={"class": "oh-input oh-select", "id": "id_department"}),
#         empty_label="---------",
#     )

#     class Meta:
#         model = Promotion
#         fields = [
#             "employee",
#             "current_status", "proposed_status",
#             "current_designation", "proposed_designation",
#             "current_cl", "current_pl", "current_sl",
#             "adjusted_cl", "adjusted_pl", "adjusted_sl",
#             "proposed_basic_salary",
#             "effective_from",
#         ]
#         widgets = {
#             # We submit hidden values for current_*; the visible fields are separate read-only inputs in the template.
#             "current_status": forms.HiddenInput(),
#             "current_designation": forms.HiddenInput(),

#             "proposed_status": forms.Select(attrs={"class": "oh-input oh-select"}),
#             "proposed_designation": forms.Select(attrs={"class": "oh-input oh-select"}),

#             "proposed_basic_salary": forms.NumberInput(attrs={"class":"oh-input","readonly":True,"step":"0.01"}),
#             "effective_from": forms.DateInput(attrs={"type":"date","class":"oh-input"}),

#             "current_cl": forms.HiddenInput(),
#             "current_pl": forms.HiddenInput(),
#             "current_sl": forms.HiddenInput(),
#             "adjusted_cl": forms.HiddenInput(),
#             "adjusted_pl": forms.HiddenInput(),
#             "adjusted_sl": forms.HiddenInput(),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Department choices
#         try:
#             self.fields["department"].queryset = Department.objects.all().order_by("department")
#         except Exception:
#             self.fields["department"].queryset = Department.objects.all()

#         # HTMX hooks
#         self.fields["employee"].widget.attrs.update({
#     "id": "id_employee",
#     "class": "oh-input oh-select",
#     "hx-get": reverse("promotion:employee_lookup"),
#     "hx-target": "#promo-emp-details",
#     "hx-trigger": "change",
#     "hx-include": "#id_employee",   # ⬅ only include this select
# })
#         self.fields["proposed_designation"].widget.attrs.update({
#             "hx-get": reverse("promotion:designation_details"),
#             "hx-target": "#promo-proposal-fields",
#             "hx-trigger": "change",
#             "hx-include": "closest form",
#         })

#         # Proposed options
#         self.fields["proposed_designation"].queryset = Designation.objects.all().order_by("name")
#         self.fields["proposed_status"].choices = [("REGULAR", "Regular"), ("CONTRACT", "Contractual")]
#         self.fields["proposed_basic_salary"].label = _("Proposed Basic Salary")
#         self.fields["effective_from"].label = _("Promotion Effective From")


# promotion/forms.py
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Promotion, Designation
from employee.models import Employee
from base.models import Department, JobPosition
from django.db import models  # for Q

class PromotionForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        label=_("Department"),
        required=False,
        widget=forms.Select(attrs={"class": "oh-input oh-select", "id": "id_department"}),
        empty_label="---------",
    )

    # ChoiceField will hold JobPosition IDs. We'll map it to a Designation in the view.
    proposed_designation = forms.ChoiceField(
        label=_("Proposed Employee New Grade/Designation"),
        required=True,
        choices=[],  # filled dynamically
        widget=forms.Select(attrs={"class": "oh-input oh-select", "id": "id_proposed_designation"}),
    )

    class Meta:
        model = Promotion
        fields = [
            "employee",
            "current_status", "proposed_status",
            "current_designation", "proposed_designation",
            "current_cl", "current_pl", "current_sl",
            "adjusted_cl", "adjusted_pl", "adjusted_sl",
            "proposed_basic_salary",
            "effective_from",
        ]
        widgets = {
            "employee": forms.Select(attrs={"class": "oh-input oh-select", "id": "id_employee"}),
            "current_status": forms.HiddenInput(),
            "current_designation": forms.HiddenInput(),
            "proposed_status": forms.Select(attrs={"class": "oh-input oh-select"}),
            "proposed_basic_salary": forms.NumberInput(attrs={"class":"oh-input","readonly":True,"step":"0.01"}),
            "effective_from": forms.DateInput(attrs={"type":"date","class":"oh-input"}),
            "current_cl": forms.HiddenInput(),
            "current_pl": forms.HiddenInput(),
            "current_sl": forms.HiddenInput(),
            "adjusted_cl": forms.HiddenInput(),
            "adjusted_pl": forms.HiddenInput(),
            "adjusted_sl": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Department options
        try:
            self.fields["department"].queryset = Department.objects.all().order_by("department")
        except Exception:
            self.fields["department"].queryset = Department.objects.all()

        # ✅ HTMX wiring
        self.fields["employee"].widget.attrs.update({
            "hx-get": reverse("promotion:employee_lookup"),
            "hx-target": "#promo-emp-details",
            "hx-trigger": "change",
            "hx-include": "#id_employee",  # send only the employee
        })
        self.fields["department"].widget.attrs.update({
            "hx-get": reverse("promotion:positions_for_department"),
            "hx-target": "#id_proposed_designation",  # update the select's options
            "hx-trigger": "change",
            "hx-include": "#id_department",
            "hx-swap": "innerHTML",
        })
        self.fields["proposed_designation"].widget.attrs.update({
            "hx-get": reverse("promotion:designation_details"),
            "hx-target": "#promo-proposal-fields",
            "hx-trigger": "change",
            "hx-include": "closest form",
        })

        # Preload options when editing / when department is already set
        dep_id = None
        if self.is_bound:
            dep_id = self.data.get("department") or self.data.get("department_id")
        else:
            dep_id = self.initial.get("department")

        opts = []
        if dep_id:
            try:
                dep_id = int(dep_id)
                positions = JobPosition.objects.filter(
                    models.Q(department_id=dep_id) | models.Q(department__id=dep_id)
                ).order_by("job_position", "name", "id")
                opts = [(p.pk, getattr(p, "job_position", None) or getattr(p, "name", str(p.pk))) for p in positions]
            except Exception:
                pass

        self.fields["proposed_designation"].choices = [("", "---------")] + opts

        # Proposed status choices
        self.fields["proposed_status"].choices = [("REGULAR", "Regular"), ("CONTRACT", "Contractual")]
