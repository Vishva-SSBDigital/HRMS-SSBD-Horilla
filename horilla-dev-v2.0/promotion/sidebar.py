# from django.urls import reverse_lazy

# # Text shown on the left sidebar section header
# MENU = "PROMOTION"

# # Relative static path for the icon used by the section header
# # Put your SVG at:  static/images/ui/promotion.svg
# # IMG_SRC = "images/ui/performance-appraisal.png"

# # Submenu items (label + target URL)
# SUBMENUS = [
#     {
#         "menu": "Create / Propose Promotion",
#         "redirect": reverse_lazy("promotion:create"),
#     },
#     # You can add more when you build the views:
#     # {"menu": "Promotion List", "redirect": reverse_lazy("promotion:list")},
#     # {"menu": "Promotion History", "redirect": reverse_lazy("promotion:history")},
# ]

from django.urls import reverse_lazy

MENU = "PROMOTION"
IMG_SRC = "images/ui/performance-appraisal.png"

SUBMENUS = [
    {"menu": "Promotion List", "redirect": reverse_lazy("promotion:employee_list")},
    {"menu": "Create Promotion", "redirect": reverse_lazy("promotion:create")},
]
