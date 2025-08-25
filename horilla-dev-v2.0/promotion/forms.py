
# from django import forms
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
# from .models import Promotion, Designation
# from employee.models import Employee
# from base.models import Department   # ← add this

# class PromotionForm(forms.ModelForm):
#     # add department as a form field (works whether or not model has FK)
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
#             # include the next line only if Promotion model actually has department FK
#             # "department",
#             "current_status",
#             "proposed_status",
#             "current_designation",
#             "proposed_designation",
#             "current_cl", "current_pl", "current_sl",
#             "adjusted_cl", "adjusted_pl", "adjusted_sl",
#             "proposed_basic_salary",
#             "effective_from",
#         ]
#         widgets = {
#             "employee": forms.Select(attrs={"class": "oh-input oh-select"}),
#             "current_status": forms.Select(attrs={"class":"oh-input", "disabled": True}),
#             "current_designation": forms.Select(attrs={"class":"oh-input", "disabled": True}),
#             "proposed_status": forms.Select(attrs={"class":"oh-input oh-select"}),
#             "proposed_designation": forms.Select(attrs={"class":"oh-input oh-select"}),
#             "proposed_basic_salary": forms.NumberInput(attrs={"class":"oh-input", "readonly": True, "step":"0.01"}),
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

#         # Populate employee dropdown (adjust ordering/fields to your schema)
#         self.fields["employee"].queryset = Employee.objects.all().order_by(
#             "employee_first_name", "employee_last_name"
#         )
#         self.fields["employee"].empty_label = "---------"

#         def label_emp(e):
#             first = getattr(e, "employee_first_name", "") or ""
#             last = getattr(e, "employee_last_name", "") or ""
#             code = getattr(e, "emp_code", "") or getattr(e, "employee_id", "") or ""
#             name = (first + " " + last).strip() or str(e)
#             return f"{name} ({code})" if code else name
#         self.fields["employee"].label_from_instance = label_emp

#         # Department options
#         # Use the right display field (department/name/title) for your model
#         try:
#             self.fields["department"].queryset = Department.objects.all().order_by("department")
#         except Exception:
#             self.fields["department"].queryset = Department.objects.all()

#         # HTMX hooks (use reverse to avoid hard-coded URLs)
#         self.fields["employee"].widget.attrs.update({
#             "hx-get": reverse("promotion:employee_lookup"),
#             "hx-target": "#promo-emp-details",
#             "hx-trigger": "change",
#             "hx-include": "closest form",
#         })
#         self.fields["proposed_designation"].widget.attrs.update({
#             "hx-get": reverse("promotion:designation_details"),
#             "hx-target": "#promo-proposal-fields",
#             "hx-trigger": "change",
#             "hx-include": "closest form",
#         })

#         # Other dropdowns
#         self.fields["proposed_designation"].queryset = Designation.objects.all().order_by("name")
#         self.fields["proposed_status"].choices = [("REGULAR", "Regular"), ("CONTRACT", "Contractual")]
#         self.fields["proposed_basic_salary"].label = _("Proposed Basic Salary")
#         self.fields["effective_from"].label = _("Promotion Effective From")
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Promotion, Designation
from employee.models import Employee
from base.models import Department


class PromotionForm(forms.ModelForm):
    # Extra, non-model field (preselect via OOB swap)
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        label=_("Department"),
        required=False,
        widget=forms.Select(attrs={"class": "oh-input oh-select", "id": "id_department"}),
        empty_label="---------",
    )

    class Meta:
        model = Promotion
        fields = [
            "employee",
            # "department",  # include only if Promotion has this FK
            "current_status",
            "proposed_status",
            "current_designation",
            "proposed_designation",
            "current_cl", "current_pl", "current_sl",
            "adjusted_cl", "adjusted_pl", "adjusted_sl",
            "proposed_basic_salary",
            "effective_from",
        ]
        widgets = {
            "employee": forms.Select(attrs={"class": "oh-input oh-select"}),
            # snapshots should POST; make them hidden (you render visible, read-only clones in the partial)
            "current_status": forms.HiddenInput(),
            "current_designation": forms.HiddenInput(),
            "proposed_status": forms.Select(attrs={"class": "oh-input oh-select"}),
            "proposed_designation": forms.Select(attrs={"class": "oh-input oh-select"}),
            "proposed_basic_salary": forms.NumberInput(attrs={"class":"oh-input", "readonly": True, "step":"0.01"}),
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

        # --- Employee dropdown ---
        # Order by 'name' (fallback to first/last if your other schema is used elsewhere)
        try:
            self.fields["employee"].queryset = Employee.objects.all().order_by("name")
        except Exception:
            # fallback if your Employee has first/last in another project
            self.fields["employee"].queryset = Employee.objects.all().order_by(
                "employee_first_name", "employee_last_name"
            )
        self.fields["employee"].empty_label = "---------"

        def label_emp(e):
            # prefer full name field
            name = getattr(e, "name", "").strip()
            if not name:
                first = getattr(e, "employee_first_name", "") or ""
                last = getattr(e, "employee_last_name", "") or ""
                name = (first + " " + last).strip() or str(e)
            code = getattr(e, "emp_code", "") or getattr(e, "employee_id", "") or ""
            return f"{name} ({code})" if code else name

        self.fields["employee"].label_from_instance = label_emp

        # --- Department options for OOB preselect ---
        try:
            self.fields["department"].queryset = Department.objects.all().order_by("department")
        except Exception:
            self.fields["department"].queryset = Department.objects.all()

        # --- HTMX hooks ---
        self.fields["employee"].widget.attrs.update({
            "hx-get": reverse("promotion:employee_lookup"),
            "hx-target": "#promo-emp-details",
            "hx-trigger": "change",
            "hx-include": "closest form",
        })
        self.fields["proposed_designation"].widget.attrs.update({
            "hx-get": reverse("promotion:designation_details"),
            "hx-target": "#promo-proposal-fields",
            "hx-trigger": "change",
            "hx-include": "closest form",
        })

        # --- Other dropdowns ---
        self.fields["proposed_designation"].queryset = Designation.objects.all().order_by("name")
        self.fields["proposed_status"].choices = [
            ("REGULAR", _("Regular")),
            ("CONTRACT", _("Contractual")),
        ]
        self.fields["proposed_basic_salary"].label = _("Proposed Basic Salary")
        self.fields["effective_from"].label = _("Promotion Effective From")
