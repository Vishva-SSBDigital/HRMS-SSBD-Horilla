# from django import forms
# from .models import Deputation, Employee
# from .models import Deputation            # ✅ from your app
# from employee.models import Employee      # ✅ NOT from .models


# class DeputationForm(forms.ModelForm):
#     class Meta:
#         model = Deputation
#         fields = [
#             "employee",
#             "designation",
#             "original_branch",
#             "deputed_to",
#             "start_date",
#             "end_date",
#             "email",
#             "current_position",
#         ]
    
#     employee = forms.ModelChoiceField(
#         queryset=Employee.objects.all(),
#         label="Employee",
#         widget=forms.Select(attrs={
#             "hx-get": "/deputation/employee-lookup/",  # HTMX request URL to fetch employee data
#             "hx-target": "#employee-details",  # ID where the response will be inserted
#             "hx-trigger": "change",  # Trigger when the employee is selected
#         })
#     )
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from .models import Deputation
# from employee.models import Employee

# class DeputationForm(forms.ModelForm):
#     # Override to attach HTMX behavior to the select
#     employee = forms.ModelChoiceField(
#         queryset=Employee.objects.all(),
#         label=_("Employee"),
#         widget=forms.Select(attrs={
#             "hx-get": "/deputation/employee-lookup/",   # ensure this path matches your urls.py
#             "hx-target": "#employee-details",
#             "hx-trigger": "change",
#         }),
#     )

#     class Meta:
#         model = Deputation
#         fields = [
#             "employee",
#             "designation",
#             "original_branch",
#             "deputed_to",
#             "start_date",
#             "end_date",
#             "email",
#             "current_position",
#         ]
#         widgets = {
#             "start_date": forms.DateInput(attrs={"type": "date"}),
#             "end_date": forms.DateInput(attrs={"type": "date"}),
#             "email": forms.EmailInput(),
#         }
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from .models import Deputation
# from employee.models import Employee

# class DeputationForm(forms.ModelForm):
#     # Attach HTMX attributes to the select widget
#     employee = forms.ModelChoiceField(
#         queryset=Employee.objects.all(),
#         label=_("Employee"),
#         widget=forms.Select(attrs={
#             "hx-get": "/deputation/employee-lookup/",   # keep in sync with urls.py
#             "hx-target": "#employee-details",
#             "hx-trigger": "change",
#         }),
#     )

#     class Meta:
#         model = Deputation
#         fields = [
#             "employee",
#             "designation",
#             "original_branch",
#             "deputed_to",
#             "start_date",
#             "end_date",
#             "email",
#             "current_position",
#         ]
#         widgets = {
#             "start_date": forms.DateInput(attrs={"type": "date"}),
#             "end_date": forms.DateInput(attrs={"type": "date"}),
#             "email": forms.EmailInput(),
            
#         }
# forms.py
# from django import forms
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
# from .models import Deputation
# from employee.models import Employee


# class DeputationForm(forms.ModelForm):
#     employee = forms.ModelChoiceField(
#         queryset=Employee.objects.all(),
#         label=_("Employee"),
#         widget=forms.Select(),  
#          # attrs set in __init__
#     )
     
#     def __init__(self, *args, **kwargs):
#         request = kwargs.pop("request", None)  # optional, not required
#         super().__init__(*args, **kwargs)

#         # Resolve the correct URL by name. (No namespace shown in your urls, so use this name)
#         lookup_url = reverse("deputation-employee-lookup")
#         # Ensure the triggering element’s value is included, and target the right container.
#         self.fields["employee"].widget.attrs.update({
#             "hx-get": lookup_url,
#             "hx-target": "#employee-details",
#             "hx-trigger": "change",
#             "hx-include": "#id_employee",  # ensures value always sent
#         })

#     class Meta:
#         model = Deputation
#         fields = [
#             "employee",
#             "designation",
#             "original_branch",
#             "deputed_to",
#             "start_date",
#             "end_date",
#             "email",
#             "current_position",
#         ]
#         widgets = {
#             "start_date": forms.DateInput(attrs={"type": "date"}),
#             "end_date": forms.DateInput(attrs={"type": "date"}),
#             "email": forms.EmailInput(),
#         }

from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Deputation
from employee.models import Employee
from base.models import Department, JobPosition  # ← ensure this import exists


class DeputationForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label=_("Employee"),
        widget=forms.Select(),
    )

    # NEW dropdowns (declare with .none(), then fill in __init__)
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        label=_("Department"),
        required=False,
        widget=forms.Select(attrs={"id": "id_department"}),
        empty_label="---------",  # shows a placeholder even if empty
    )

    deputed_designation = forms.ModelChoiceField(
        queryset=JobPosition.objects.none(),
        label=_("Deputed Designation"),
        required=False,
        widget=forms.Select(attrs={"id": "id_deputed_designation"}),
        empty_label="---------",
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # HTMX for employee lookup (unchanged)
        lookup_url = reverse("deputation-employee-lookup")
        self.fields["employee"].widget.attrs.update({
            "hx-get": lookup_url,
            "hx-target": "#employee-details",
            "hx-trigger": "change",
            "hx-include": "#id_employee",
        })

        # Fill dropdowns here (safe—no DB at import time)
        try:
            self.fields["department"].queryset = Department.objects.all().order_by("department")
        except Exception:
            self.fields["department"].queryset = Department.objects.all()

        try:
            # Use Horilla’s typical field name
            self.fields["deputed_designation"].queryset = JobPosition.objects.all().order_by("job_position")
        except Exception:
            self.fields["deputed_designation"].queryset = JobPosition.objects.all()

    class Meta:
        model = Deputation
        fields = [
            "employee",
            "designation",
            "original_branch",
            "deputed_to",
            "start_date",
            "end_date",
            "email",
            "current_position",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "email": forms.EmailInput(),
        }



# # deputation/forms.py
# from django import forms
# from employee.models import Employee           # <- import from employee app
# from .models import Deputation

# class DeputationForm(forms.ModelForm):
#     employee = forms.ModelChoiceField(
#         queryset=Employee.objects.all(),
#         label="Employee",
#         widget=forms.Select(attrs={
#             "hx-get": "/deputation/employee-lookup/",
#             "hx-target": "#employee-details",
#             "hx-trigger": "change",
#         }),
#     )

#     class Meta:
#         model = Deputation
#         fields = [
#             "employee",
#             "designation",
#             "original_branch",
#             "deputed_to",
#             "start_date",
#             "end_date",
#             "email",
#             "current_position",
#         ]
