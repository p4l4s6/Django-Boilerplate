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


def generate_code():
    code = str(random.randint(100000, 999999))
    while UserConfirmation.objects.filter(confirmation_code=code).exists():
        code = str(random.randint(100000, 999999))
    return code


def get_user(email):
    return User.objects.get(email=email)


def create_user_confirmation(user, ip_address):
    confirmation_code = UserConfirmation.objects.create(
        identifier=user.email,
        ip_address=ip_address,
        confirmation_code=generate_code())
    confirmation_code.save()
    return confirmation_code


def regenerate_token(user):
    token, created = Token.objects.get_or_create(user=user)
    if not created:
        token.delete()
    return Token.objects.get_or_create(user=user)


def is_code_valid(identifier, code):
    try:
        otp_code = get_code(identifier, code)
        return True
    except ObjectDoesNotExist:
        return False


def get_code(identifier, code):
    return UserConfirmation.objects.get(identifier=identifier, is_used=False, confirmation_code=code)


def validate_user(user):
    # if not user.is_verified:
    #     raise serializers.ValidationError({'email': 'You are not verified'})
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


def process_code(identifier):
    code = generate_code()
    confirmation = UserConfirmation.objects.create(identifier=identifier, confirmation_code=code)
    confirmation.save()
    data = {
        'email': identifier,
        'code': confirmation.confirmation_code
    }
    return data


def get_full_image_url(request, photo_url):
    return request.build_absolute_uri(photo_url)
