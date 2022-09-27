from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from coreapp import constants
from coreapp.manager import MyUserManager
from .base import BaseModel


# Create your models here.

class Country(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    phone_code = models.CharField(_("Phone code"), max_length=50)
    flag = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(unique=True, max_length=20)
    dob = models.DateField()
    image = models.ForeignKey('coreapp.Document', on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.SmallIntegerField(choices=constants.GenderChoices.choices, default=constants.GenderChoices.MALE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(blank=True)
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @cached_property
    def get_image_url(self):
        return self.image.get_url if self.image_id else None

    @cached_property
    def get_country_name(self):
        return self.country.name


class UserConfirmation(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.confirmation_code} : {self.is_used}"


class LoginHistory(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=100)
    user_agent = models.CharField(max_length=500)
    is_success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.ip_address} - {self.user_agent} - {self.is_success}"


class Document(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.FileField(upload_to='documents/%Y/%m/%d/')
    doc_type = models.SmallIntegerField(choices=constants.DocumentChoices.choices)

    def __str__(self):
        return f"{self.owner} - {self.document.name}"

    @cached_property
    def get_url(self):
        return f"{settings.MEDIA_HOST}{self.document.url}"
