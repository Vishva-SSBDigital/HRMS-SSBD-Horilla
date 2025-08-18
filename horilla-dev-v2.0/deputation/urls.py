# from django.urls import path
# from deputation.views import hello_world
# from deputation.cbv import employees
# from deputation import views

# urlpatterns = [
# path('view-employee/', hello_world, name="deputation_employee_view"),
# path("deputation-employee-list",employees.DeputationEmployeeList.as_view(),name="deputation_employee_list"),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path("", views.deputation_list, name="deputation-list"),
    # 🔽 alias so reverse('deputation_employee_view') works
    path("employee/", views.deputation_list, name="deputation_employee_view"),
    path("create/", views.create_deputation, name="deputation-create"),
    path("<int:pk>/update/", views.deputation_update, name="deputation-update"),
    path("<int:pk>/delete/", views.deputation_delete, name="deputation-delete"),
    path("employee-lookup/", views.employee_lookup, name="deputation-employee-lookup"),


] 
    # path("create/", views.deputation_create_view, name="deputation-create"),
    # path("employee/lookup/", views.employee_lookup, name="employee_lookup"),

    # deputation/urls.py


