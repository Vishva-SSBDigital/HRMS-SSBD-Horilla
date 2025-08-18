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
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Deputation
from employee.models import Employee

class DeputationForm(forms.ModelForm):
    # Attach HTMX attributes to the select widget
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label=_("Employee"),
        widget=forms.Select(attrs={
            "hx-get": "/deputation/employee-lookup/",   # keep in sync with urls.py
            "hx-target": "#employee-details",
            "hx-trigger": "change",
        }),
    )

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
