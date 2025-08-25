
from django.urls import path
from . import views

app_name = "promotion"

urlpatterns = [
    # list
    path("employee/", views.PromotionListView.as_view(), name="employee_list"),

    # modal form (create/update)
    path("create/", views.promotion_create, name="create"),
    path("update/<int:pk>/", views.promotion_update, name="update"),
    path("delete/<int:pk>/", views.promotion_delete, name="delete"),

    # HTMX helpers (we already built these earlier)
    path("employee-lookup/", views.employee_lookup, name="employee_lookup"),
    path("designation-details/", views.designation_details, name="designation_details"),
    # promotion/urls.py
    path("positions-for-department/", views.positions_for_department, name="positions_for_department"),

   
]
