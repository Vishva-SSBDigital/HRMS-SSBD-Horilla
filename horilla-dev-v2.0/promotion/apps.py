from django.apps import AppConfig



class PromotionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "promotion"   # <— must match the Python package name
    verbose_name = "Promotion Management"
