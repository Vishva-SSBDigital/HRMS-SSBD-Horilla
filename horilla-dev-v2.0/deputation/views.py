# # deputation/views.py
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.db.models import Q
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
# from .models import Employee


# from .forms import DeputationForm
# from .models import Deputation


# def _is_htmx(request) -> bool:
#     """
#     True if the request came from HTMX.
#     Works with both modern headers and Django's META.
#     """
#     return request.headers.get("HX-Request") == "true" or bool(request.META.get("HTTP_HX_REQUEST"))


# @login_required
# def deputation_list(request):
#     """
#     List deputations with search, branch & status filters, and pagination.
#     Designed to work both as a full-page render and as an HTMX fragment refresh.
#     """
#     q = (request.GET.get("q") or "").strip()
#     branch = (request.GET.get("branch") or "").strip()
#     status = (request.GET.get("status") or "all").strip()

#     # per-page safety
#     try:
#         per_page = int(request.GET.get("per_page") or 20)
#     except (TypeError, ValueError):
#         per_page = 20

#     page = request.GET.get("page") or 1

#     qs = Deputation.objects.select_related("employee").order_by("-id")

#     if q:
#         qs = qs.filter(
#             Q(employee__employee_first_name__icontains=q)
#             | Q(employee__employee_last_name__icontains=q)
#             | Q(email__icontains=q)
#             | Q(original_branch__icontains=q)
#             | Q(deputed_to__icontains=q)
#             | Q(designation__icontains=q)
#             | Q(current_position__icontains=q)
#         )

#     if branch:
#         qs = qs.filter(original_branch__icontains=branch)

#     # status: "all" | "ongoing" | "ended"
#     if status == "ongoing":
#         qs = qs.filter(end_date__isnull=True)
#     elif status == "ended":
#         qs = qs.filter(end_date__isnull=False)

#     paginator = Paginator(qs, per_page)
#     try:
#         page_obj = paginator.get_page(page)
#     except (PageNotAnInteger, EmptyPage):
#         page_obj = paginator.get_page(1)

#     ctx = {
#         "page_obj": page_obj,
#         "q": q,
#         "branch": branch,
#         "status": status,
#         "per_page": per_page,
#         "total_count": paginator.count,
#     }

#     # If you decide to render a smaller fragment for HTMX updates,
#     # uncomment the next two lines and create the template:
#     # if _is_htmx(request):
#     #     return render(request, "deputation/_table.html", ctx)

#     return render(request, "deputation/deputation_list.html", ctx)

# def create_deputation(request):
#     employees = Employee.objects.all()
#     initial = {}

#     emp_id = request.GET.get("employee_id")
#     if emp_id:
#         try:
#             emp = Employee.objects.get(pk=emp_id)
#             initial = {
#                 "employee": emp.id,
#                 "designation": emp.designation,
#                 "original_branch": emp.branch,
#                 "email": emp.email,              # <-- was email_id; correct key is email
#                 "current_position": emp.current_position,
#             }
#         except Employee.DoesNotExist:
#             pass

#     if request.method == "POST":
#         form = DeputationForm(request.POST)
#         if form.is_valid():
#             obj = form.save()
#             if _is_htmx(request):
#                 resp = HttpResponse(status=204)
#                 resp["HX-Trigger"] = "deputation:created"
#                 return resp
#             messages.success(request, _("Deputation created successfully."))
#             return redirect("deputation-list")
#     else:
#         form = DeputationForm(initial=initial)

#     return render(request, "deputation/deputation_form.html", {
#         "form": form,
#         "employees": employees,
#         "is_update": False,
#     })

# # def create_deputation(request):
# #     employees = Employee.objects.all()
# #     initial = {}

# #     # If user clicked "Load" button after selecting employee
# #     emp_id = request.GET.get("employee_id")
# #     if emp_id:
# #         try:
# #             emp = Employee.objects.get(pk=emp_id)
# #             initial = {
# #                 "employee": emp.id,
# #                 "designation": emp.designation,
# #                 "original_branch": emp.branch,
# #                 "email_id": emp.email,
# #                 "current_position": emp.current_position,
# #             }
# #         except Employee.DoesNotExist:
# #             pass

# #     # If POST → save form
# #     if request.method == "POST":
# #         form = DeputationForm(request.POST)
# #         if form.is_valid():
# #             form.save()
# #             return redirect("deputation-list")  # change to your list view name
# #     else:
# #         form = DeputationForm(initial=initial)

# #     return render(request, "deputation/deputation_form.html", {
# #         "form": form,
# #         "employees": employees,
# #     })
# @login_required
# def deputation_update(request, pk):
#     instance = get_object_or_404(Deputation, pk=pk)
#     if request.method == "POST":
#         form = DeputationForm(request.POST, instance=instance)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Deputation updated successfully."))
#             return redirect("deputation-list")
#     else:
#         form = DeputationForm(instance=instance)
#     return render(
#         request,
#         "deputation/deputation_form.html",
#         {"form": form, "is_update": True, "instance": instance},  # <-- pass instance
#     )



# @login_required
# def deputation_delete(request, pk):
#     if request.method != "POST":
#         return redirect("deputation-list")
#     instance = get_object_or_404(Deputation, pk=pk)
#     instance.delete()
#     if _is_htmx(request):
#         # 204 No Content lets us remove the row client-side
#         return HttpResponse(status=204)
#     messages.success(request, _("Deputation deleted successfully."))
#     return redirect("deputation-list")

# @login_required
# def employee_lookup(request):
#     """
#     HTMX endpoint. Expects ?employee_id=<pk>
#     Returns an HTML partial with prefilled inputs for designation and original branch.
#     """
#     emp_id = request.GET.get("employee_id")
#     employee = get_object_or_404(Employee, pk=emp_id) if emp_id else None

#     ctx = {
#         "designation": employee.designation if employee else "",
#         "original_branch": employee.branch if employee else "",
#     }
#     return render(request, "deputation/_employee_autofill_fields.html", ctx)
# deputation/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from employee.models import Employee            # ✅ correct import
from .forms import DeputationForm
from .models import Deputation


def _is_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true" or bool(request.META.get("HTTP_HX_REQUEST"))

def _text(v):
    """Return a nice string for plain values or related objects."""
    if v is None:
        return ""
    # direct primitives
    if isinstance(v, (str, int, float)):
        return str(v)
    # common label attrs on related objects
    for attr in ("name", "title", "display_name", "branch_name", "department_name"):
        if hasattr(v, attr):
            val = getattr(v, attr)
            if val:
                return str(val)
    # fallback to __str__
    s = str(v)
    return "" if s == "None" else s

def _first(*vals):
    """First non-empty string."""
    for v in vals:
        if v not in (None, "", "None"):
            return str(v)
    return ""
@login_required
def deputation_list(request):
    q = (request.GET.get("q") or "").strip()
    branch = (request.GET.get("branch") or "").strip()
    status = (request.GET.get("status") or "all").strip()

    try:
        per_page = int(request.GET.get("per_page") or 20)
    except (TypeError, ValueError):
        per_page = 20

    page = request.GET.get("page") or 1

    qs = Deputation.objects.select_related("employee").order_by("-id")

    if q:
        qs = qs.filter(
            Q(employee__employee_first_name__icontains=q)
            | Q(employee__employee_last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(original_branch__icontains=q)
            | Q(deputed_to__icontains=q)
            | Q(designation__icontains=q)
            | Q(current_position__icontains=q)
        )

    if branch:
        qs = qs.filter(original_branch__icontains=branch)

    # Better semantics for status:
    today = timezone.localdate()
    if status == "ongoing":
        qs = qs.filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
    elif status == "ended":
        qs = qs.filter(end_date__lt=today)

    paginator = Paginator(qs, per_page)
    try:
        page_obj = paginator.get_page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    ctx = {
        "page_obj": page_obj,
        "q": q,
        "branch": branch,
        "status": status,
        "per_page": per_page,
        "total_count": paginator.count,
    }

    return render(request, "deputation/deputation_list.html", ctx)


@login_required
def create_deputation(request):
    employees = Employee.objects.all()
    initial = {}

    emp_id = request.GET.get("employee_id")
    if emp_id:
        try:
            emp = Employee.objects.get(pk=emp_id)
            initial = {
                "employee": emp.id,
                "designation": emp.designation,
                "original_branch": emp.branch,
                "email": emp.email,
                "current_position": emp.current_position,
            }
        except Employee.DoesNotExist:
            pass

    if request.method == "POST":
        data = request.POST.copy()

        # If your form used employee_id in the select, map it:
        if data.get("employee_id") and not data.get("employee"):
            data["employee"] = data["employee_id"]

        # Blank optional end_date -> None
        if data.get("end_date", "").strip() == "":
            data["end_date"] = None

        # form = DeputationForm(data)
        form = DeputationForm(data, request=request) 
        if form.is_valid():
            obj = form.save(commit=False)

            # If your HorillaModel requires company_id, set it from employee
            if hasattr(obj, "company_id") and not obj.company_id and obj.employee_id:
                emp = getattr(obj, "employee", None)
                if emp and hasattr(emp, "company_id"):
                    obj.company_id = emp.company_id

            obj.save()

            # Show success message
            messages.success(request, _("Deputation created successfully."))

            # If HTMX request, send response without redirect
            if _is_htmx(request):
                resp = HttpResponse(status=204)
                resp["HX-Trigger"] = "deputation:created"
                return resp

            return redirect("deputation-list")
        # fall-through renders errors
    else:
        form = DeputationForm(initial=initial, request=request)
    return render(
        request,
        "deputation/deputation_form.html",
        {"form": form, "employees": employees, "is_update": False},
    )

@login_required
def deputation_update(request, pk):
    instance = get_object_or_404(Deputation, pk=pk)
    if request.method == "POST":
        data = request.POST.copy()
        if data.get("end_date", "").strip() == "":
            data["end_date"] = None
        # form = DeputationForm(data, instance=instance)
        form = DeputationForm(data, instance=instance, request=request) 
        if form.is_valid():
            obj = form.save(commit=False)
            if hasattr(obj, "company_id") and not obj.company_id and obj.employee_id:
                emp = getattr(obj, "employee", None)
                if emp and hasattr(emp, "company_id"):
                    obj.company_id = emp.company_id
            obj.save()

            if _is_htmx(request):
                resp = HttpResponse(status=204)
                resp["HX-Trigger"] = "deputation:updated"
                return resp

            messages.success(request, _("Deputation updated successfully."))
            return redirect("deputation-list")
    else:
        # form = DeputationForm(instance=instance)
        form = DeputationForm(instance=instance, request=request) 

    return render(
        request,
        "deputation/deputation_form.html",
        {"form": form, "is_update": True, "instance": instance},
    )


@login_required
def deputation_delete(request, pk):
    if request.method != "POST":
        return redirect("deputation-list")
    instance = get_object_or_404(Deputation, pk=pk)
    instance.delete()
    if _is_htmx(request):
        return HttpResponse(status=204)
    messages.success(request, _("Deputation deleted successfully."))
    return redirect("deputation-list")


# @login_required
# def employee_lookup(request):
#     emp_id = request.GET.get("employee") or request.GET.get("employee_id")
#     emp = get_object_or_404(Employee, pk=emp_id) if emp_id else None

#     # Try several likely field names/relations; pick the first that exists
#     designation = _first(
#         getattr(emp, "designation", None),
#         getattr(emp, "job_position", None),
#         getattr(emp, "position", None),
#     )

#     original_branch = _first(
#         _text(getattr(emp, "branch", None)),
#         _text(getattr(emp, "work_location", None)),
#         _text(getattr(emp, "office", None)),
#         _text(getattr(emp, "department", None)),
#     )

#     email = _first(
#         getattr(emp, "email", None),
#         getattr(emp, "official_email", None),
#         getattr(emp, "work_email", None),
#         getattr(emp, "personal_email", None),
#     )

#     current_position = _first(
#         _text(getattr(emp, "current_position", None)),
#         designation,  # fallback
#     )

#     ctx = {
#         "designation": designation,
#         "original_branch": original_branch,
#         "email": email,
#         "current_position": current_position,
#     }
#     return render(request, "deputation/_employee_autofill_fields.html", ctx)
# views.py (replace employee_lookup with this version)
# views.py (replace helpers with these)


def _label(x):
    if x is None: return ""
    if isinstance(x, (str, int, float)): return str(x)
    # try common label attrs on FK objects
    for a in ("name","title","job_position","job_role","branch_name","department_name","code"):
        if hasattr(x, a) and getattr(x, a):
            return str(getattr(x, a))
    s = str(x)
    return "" if s == "None" else s

@login_required
def employee_lookup(request):
    """
    Returns a small HTML fragment prefilled from EmployeeWorkInformation.
    HTMX GET expects ?employee=<id> (or ?employee_id=).
    """
    emp_id = request.GET.get("employee") or request.GET.get("employee_id")
    if not emp_id:
        return render(request, "deputation/_employee_autofill_fields.html", {
            "designation": "", "original_branch": "", "email": "", "current_position": "",
        })

    emp = get_object_or_404(Employee, pk=emp_id)
    wi: EmployeeWorkInformation | None = getattr(emp, "employee_work_info", None)

    # If the employee has no work info yet, return blanks (that’s expected for new data)
    if wi is None:
        return render(request, "deputation/_employee_autofill_fields.html", {
            "designation": "", "original_branch": "", "email": "", "current_position": "",
        })

    # ---- Map from EmployeeWorkInformation ----
    # job_position_id / job_role_id / department_id are FKs in your codebase
    designation      = _label(getattr(wi, "job_position_id", None))
    current_position = _label(getattr(wi, "job_role_id", None)) or designation

    # Location/branch: your WorkInfo has a text field `location` (and also department/company FKs)
    original_branch  = (
        getattr(wi, "location", "") or
        _label(getattr(wi, "department_id", None)) or
        _label(getattr(wi, "company_id", None))
    )

    # Official email for work use lives on WorkInformation
    email = getattr(wi, "email", "") or getattr(emp, "email", "")

    return render(request, "deputation/_employee_autofill_fields.html", {
        "designation": designation or "",
        "original_branch": original_branch or "",
        "email": email or "",
        "current_position": current_position or "",
    })