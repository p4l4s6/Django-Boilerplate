from django.db import models
from django.utils.translation import gettext_lazy as _


# Page  Options
class PageType(models.IntegerChoices):
    PRIVACY_POLICY = 0, _("Privacy Policy")
    TERMS_AND_CONDITION = 1, _("Terms and Condition")
    ABOUT_US = 2, _("About Us")
    GENERAL = 3, _("General")


# Payment Status
class PaymentStatus(models.IntegerChoices):
    PENDING = 0, _("Pending")
    SUCCESS = 1, _("Success")
    CANCELLED = 2, _("Cancelled")
    FAILED = 3, _("Failed")


# Payment Method
class PaymentMethod(models.IntegerChoices):
    PAYPAL = 0, _("Paypal")
    BILLPLZ = 1, _("BillPlz")
    CASH = 2, _("Cash")
