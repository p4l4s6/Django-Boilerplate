from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from coreapp import constants
from coreapp.manager import MyUserManager
from .base import BaseModel


# Create your models here.

class Country(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True)
    mobile = models.CharField(unique=True, max_length=20)
    image = models.ForeignKey('coreapp.Document', on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.SmallIntegerField(
        choices=constants.GenderChoices.choices,
        blank=True, null=True
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    wallet = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_client = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    @property
    def name(self):
        full_name = self.get_full_name()
        if not full_name.isalnum():
            return ''.join(e for e in self.first_name if e.isalnum()) \
                   + ''.join(e for e in self.last_name if e.isalnum())
        return full_name

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name


class UserConfirmation(BaseModel):
    identifier = models.CharField(max_length=100)
    confirmation_code = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.identifier} - {self.confirmation_code} : {self.is_used}"


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
