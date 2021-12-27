from django.db import models
from django.utils.translation import gettext_lazy as _


# Gender  Options
class GenderChoices(models.IntegerChoices):
    MALE = 0, _("Male")
    FEMALE = 1, _("Female")
    OTHER = 2, _("Other")


# Document  Options
class DocumentChoices(models.IntegerChoices):
    IMAGE = 0, _("Image")
    VIDEO = 1, _("Video")
    FILE = 2, _("File")
    OTHER = 3, _("Other")
