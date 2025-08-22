# from django.shortcuts import render
# from decimal import Decimal
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.db import transaction
# from django.http import JsonResponse, Http404, HttpResponseBadRequest
# from django.shortcuts import get_object_or_404, redirect, render
# from django.template.loader import render_to_string
# from django.views.generic import CreateView

# from .forms import PromotionForm
# from .models import (
#     Promotion, Employee, Designation, LeaveBalance, LeaveEntitlement, SalaryBand
# )

# # -------- Helpers --------

# def _compute_adjusted_leave(current_lb: LeaveBalance, new_ent: LeaveEntitlement):
#     """
#     Simple rule: adjusted = min(current_balance, new_entitlement)
#     You can replace with any bank policy.
#     """
#     return {
#         "cl": min(current_lb.cl_balance, new_ent.cl_per_year) if current_lb else 0,
#         "pl": min(current_lb.pl_balance, new_ent.pl_per_year) if current_lb else 0,
#         "sl": min(current_lb.sl_balance, new_ent.sl_per_year) if current_lb else 0,
#     }

# def _default_basic_for(designation: Designation) -> Decimal:
#     band = getattr(designation, "salary_band", None)
#     return band.default_basic if band else Decimal("0.00")


# # -------- HTMX endpoints --------

# @login_required
# def employee_lookup(request):
#     """
#     GET ?employee_id=E123
#     Returns partial HTML that fills name, current status/designation, current leave.
#     """
#     emp_id = request.GET.get("employee_id", "").strip()
#     if not emp_id:
#         return HttpResponseBadRequest("Missing employee_id")

#     try:
#         employee = Employee.objects.select_related("designation").get(employee_id=emp_id)
#     except Employee.DoesNotExist:
#         return JsonResponse({"ok": False, "html": "<div class='text-danger'>Employee not found</div>"})

#     lb = LeaveBalance.objects.filter(employee=employee).first()

#     context = {
#         "employee": employee,
#         "lb": lb,
#     }
#     html = render_to_string("promotion/_employee_fetch_result.html", context, request=request)
#     return JsonResponse({"ok": True, "html": html, "employee_pk": employee.pk})


# @login_required
# def designation_details(request):
#     """
#     GET with proposed_designation + employee_pk
#     Returns partial HTML to fill adjusted leave + proposed basic salary.
#     """
#     try:
#         desig_id = int(request.GET.get("proposed_designation"))
#         emp_pk = int(request.GET.get("employee"))
#     except (TypeError, ValueError):
#         return HttpResponseBadRequest("Invalid params")

#     employee = get_object_or_404(Employee, pk=emp_pk)
#     new_desig = get_object_or_404(Designation, pk=desig_id)
#     lb = LeaveBalance.objects.filter(employee=employee).first()
#     ent = LeaveEntitlement.objects.filter(designation=new_desig).first()

#     adjusted = {"cl": 0, "pl": 0, "sl": 0}
#     if ent and lb:
#         adjusted = _compute_adjusted_leave(lb, ent)

#     proposed_basic = _default_basic_for(new_desig)

#     context = {
#         "adjusted": adjusted,
#         "proposed_basic": proposed_basic,
#     }
#     html = render_to_string("promotion/_proposal_fields.html", context, request=request)
#     return JsonResponse({"ok": True, "html": html})


# # -------- Create view --------

# class PromotionCreateView(LoginRequiredMixin, CreateView):
#     model = Promotion
#     form_class = PromotionForm
#     template_name = "promotion/create.html"

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         return ctx

#     def form_valid(self, form):
#         # Must have employee set via lookup
#         employee_pk = form.cleaned_data.get("employee").pk if form.cleaned_data.get("employee") else None
#         if not employee_pk:
#             form.add_error("employee_id", "Fetch a valid Employee first.")
#             return self.form_invalid(form)

#         form.instance.created_by = self.request.user

#         # Keep a snapshot of current leave if available
#         lb = LeaveBalance.objects.filter(employee_id=employee_pk).first()
#         form.instance.current_cl = lb.cl_balance if lb else 0
#         form.instance.current_pl = lb.pl_balance if lb else 0
#         form.instance.current_sl = lb.sl_balance if lb else 0

#         messages.success(self.request, "Promotion proposal saved. Click 'Apply' to commit changes.")
#         return super().form_valid(form)

#     def get_success_url(self):
#         return self.request.build_absolute_uri(
#             f"/promotion/apply/{self.object.pk}/"
#         )


# @login_required
# @transaction.atomic
# def apply_promotion(request, pk: int):
#     """
#     Commits the promotion:
#       - Update Employee status, designation
#       - Update LeaveBalance to adjusted values
#     """
#     promo = get_object_or_404(
#         Promotion.objects.select_for_update(), pk=pk, applied=False
#     )
#     employee = promo.employee

#     # Update employee
#     employee.status = promo.proposed_status
#     employee.designation = promo.proposed_designation
#     employee.save(update_fields=["status", "designation"])

#     # Update leave balances
#     lb, _ = LeaveBalance.objects.get_or_create(employee=employee)
#     lb.cl_balance = promo.adjusted_cl
#     lb.pl_balance = promo.adjusted_pl
#     lb.sl_balance = promo.adjusted_sl
#     lb.save()

#     promo.applied = True
#     promo.save(update_fields=["applied"])

#     messages.success(request, "Promotion applied successfully.")
#     return redirect("promotion:create")


# # Create your views here.
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.html import format_html, format_html_join
from django.db import transaction
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from base.models import Department
from .models import Employee, LeaveBalance 

from .forms import PromotionForm
from .models import (
    Promotion,
    Employee,
    Designation,
    LeaveBalance,
    LeaveEntitlement,
    SalaryBand,
)

# -------------------------------------------------------------------
# LIST PAGE (Horilla style like your deputation list)
# -------------------------------------------------------------------

class PromotionListView(LoginRequiredMixin, ListView):
    model = Promotion
    template_name = "promotion/promotion_list.html"
    context_object_name = "page_obj"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Promotion.objects.select_related(
                "employee", "current_designation", "proposed_designation"
            )
            .order_by("-created_at")
        )

        q = self.request.GET.get("q") or ""
        status = self.request.GET.get("status") or "all"

        if q:
            # Adjust this filter to match your Employee fields (name, emp_code, etc.)
            qs = qs.filter(employee__name__icontains=q)

        if status == "applied":
            qs = qs.filter(applied=True)
        elif status == "pending":
            qs = qs.filter(applied=False)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q") or ""
        ctx["status"] = self.request.GET.get("status") or "all"
        ctx["per_page"] = self.paginate_by
        return ctx


# -------------------------------------------------------------------
# MODAL: CREATE
# -------------------------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def promotion_create(request):
    if request.method == "GET":
        form = PromotionForm()
        return render(
            request,
            "promotion/promotion_form.html",
            {"form": form, "is_update": False},
        )

    # POST
    form = PromotionForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            promo = form.save(commit=False)
            promo.created_by = request.user

            # snapshot current leave at creation time
            lb = LeaveBalance.objects.filter(employee=promo.employee).first()
            promo.current_cl = lb.cl_balance if lb else 0
            promo.current_pl = lb.pl_balance if lb else 0
            promo.current_sl = lb.sl_balance if lb else 0

            promo.save()

        messages.success(request, "Promotion created.")
        resp = render(
            request,
            "promotion/promotion_form.html",
            {"form": PromotionForm(), "is_update": False, "created": True},
        )
        resp["HX-Trigger"] = "promotion:created"
        return resp

    return render(
        request,
        "promotion/promotion_form.html",
        {"form": form, "is_update": False},
    )


# -------------------------------------------------------------------
# MODAL: UPDATE
# -------------------------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def promotion_update(request, pk: int):
    promo = get_object_or_404(Promotion, pk=pk)

    if request.method == "GET":
        form = PromotionForm(instance=promo)
        return render(
            request,
            "promotion/promotion_form.html",
            {"form": form, "is_update": True, "instance": promo},
        )

    form = PromotionForm(request.POST, instance=promo)
    if form.is_valid():
        form.save()
        messages.success(request, "Promotion updated.")
        resp = render(
            request,
            "promotion/promotion_form.html",
            {"form": form, "is_update": True, "instance": promo, "updated": True},
        )
        resp["HX-Trigger"] = "promotion:updated"
        return resp

    return render(
        request,
        "promotion/promotion_form.html",
        {"form": form, "is_update": True, "instance": promo},
    )


# -------------------------------------------------------------------
# INLINE DELETE (HTMX removes the row)
# -------------------------------------------------------------------

@login_required
@require_http_methods(["POST"])
def promotion_delete(request, pk: int):
    promo = get_object_or_404(Promotion, pk=pk)
    promo.delete()
    return HttpResponse("")


# -------------------------------------------------------------------
# HELPERS used by HTMX endpoints
# -------------------------------------------------------------------

def _compute_adjusted_leave(current_lb, new_ent):
    """
    Simple policy:
      adjusted = min(current balance, new entitlement)
    Customize this if your policy differs.
    """
    if not current_lb or not new_ent:
        return {"cl": 0, "pl": 0, "sl": 0}
    return {
        "cl": min(current_lb.cl_balance, new_ent.cl_per_year),
        "pl": min(current_lb.pl_balance, new_ent.pl_per_year),
        "sl": min(current_lb.sl_balance, new_ent.sl_per_year),
    }


def _default_basic_for(designation):
    if not designation:
        return Decimal("0.00")
    band = getattr(designation, "salary_band", None)
    return band.default_basic if band else Decimal("0.00")


# -------------------------------------------------------------------
# HTMX: EMPLOYEE LOOKUP
# Accepts either employee=<pk> (select) or employee_id=<code> (textbox)
# Returns JSON with rendered partial for autofill block
# -------------------------------------------------------------------

@login_required
def employee_lookup(request):
    emp_pk = request.GET.get("employee")
    emp_code = (request.GET.get("employee_id") or "").strip()

    employee = None
    if emp_pk:
        try:
            employee = Employee.objects.select_related("designation").get(pk=emp_pk)
        except Employee.DoesNotExist:
            employee = None
    elif emp_code:
        try:
            employee = Employee.objects.select_related("designation").get(
                employee_id=emp_code
            )
        except Employee.DoesNotExist:
            employee = None

    if not employee:
        return JsonResponse(
            {"ok": False, "html": "<div class='oh-input__error'>Employee not found</div>"}
        )

    lb = LeaveBalance.objects.filter(employee=employee).first()

    html = render_to_string(
        "promotion/_employee_autofill_fields.html",
        {"employee": employee, "lb": lb},
        request=request,
    )
    return JsonResponse({"ok": True, "html": html})


# -------------------------------------------------------------------
# HTMX: DESIGNATION DETAILS
# Needs proposed_designation=<id> and employee=<pk>
# Returns JSON with rendered partial for adjusted leaves + proposed basic
# -------------------------------------------------------------------

@login_required
def designation_details(request):
    try:
        desig_id = int(request.GET.get("proposed_designation"))
        emp_pk = int(request.GET.get("employee"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid parameters")

    employee = get_object_or_404(Employee, pk=emp_pk)
    new_desig = get_object_or_404(Designation, pk=desig_id)

    lb = LeaveBalance.objects.filter(employee=employee).first()
    ent = LeaveEntitlement.objects.filter(designation=new_desig).first()

    adjusted = _compute_adjusted_leave(lb, ent)
    proposed_basic = _default_basic_for(new_desig)

    html = render_to_string(
        "promotion/_proposal_fields.html",
        {"adjusted": adjusted, "proposed_basic": proposed_basic},
        request=request,
    )
    return JsonResponse({"ok": True, "html": html})

@login_required
def employee_lookup(request):
    emp_pk = request.GET.get("employee")
    emp_code = (request.GET.get("employee_id") or "").strip()

    employee = None
    if emp_pk:
        try:
            employee = Employee.objects.select_related("designation", "department").get(pk=emp_pk)
        except Employee.DoesNotExist:
            employee = None
    elif emp_code:
        try:
            employee = Employee.objects.select_related("designation", "department").get(employee_id=emp_code)
        except Employee.DoesNotExist:
            employee = None

    if not employee:
        return HttpResponse("<div class='oh-input__error'>Employee not found</div>")

    lb = LeaveBalance.objects.filter(employee=employee).first()
    departments = Department.objects.all().order_by("department")  # or "name"

    html = render_to_string(
        "promotion/_employee_autofill_fields.html",
        {"employee": employee, "lb": lb, "departments": departments},
        request=request,
    )
    return HttpResponse(html)

@login_required
def designation_details(request):
    try:
        desig_id = int(request.GET.get("proposed_designation"))
        emp_pk = int(request.GET.get("employee"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid parameters")

    employee = get_object_or_404(Employee, pk=emp_pk)
    new_desig = get_object_or_404(Designation, pk=desig_id)
    lb = LeaveBalance.objects.filter(employee=employee).first()
    ent = LeaveEntitlement.objects.filter(designation=new_desig).first()

    adjusted = _compute_adjusted_leave(lb, ent)
    proposed_basic = _default_basic_for(new_desig)

    html = render_to_string(
        "promotion/_proposal_fields.html",
        {"adjusted": adjusted, "proposed_basic": proposed_basic},
        request=request,
    )
    return HttpResponse(html)
