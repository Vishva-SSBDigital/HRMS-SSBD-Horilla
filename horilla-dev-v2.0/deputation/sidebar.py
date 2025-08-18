from django.urls import reverse_lazy


MENU = "DEPUTATION"
IMG_SRC = "images/ui/depution.svg"

SUBMENUS = [
    {
        "menu" : "Deputation List",
        "redirect" : reverse_lazy("deputation_employee_view")

    }
]
