import random

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from coreapp.models import UserConfirmation, User


def get_client_info(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')
    return ip, user_agent


def get_user_by_email(email):
    return User.objects.get(email=email)


def get_user_by_mobile(mobile):
    return User.objects.get(mobile=mobile)


def regenerate_token(user):
    token, created = Token.objects.get_or_create(user=user)
    if not created:
        token.delete()
    return Token.objects.get_or_create(user=user)


def validate_user(user):
    if not user.is_verified:
        raise serializers.ValidationError({'email': 'You are not verified'})
    if not user.is_active:
        raise serializers.ValidationError({'email': [_("Your account has been disabled by administrator"), ]})


def validate_user_password(password):
    try:
        validate_password(password)
    except ValidationError as e:
        raise serializers.ValidationError({'password': e.error_list})


def check_approval(user):
    if not user.is_approved:
        raise serializers.ValidationError({'email': [_("Your account has not been approved by yet"), ]})
