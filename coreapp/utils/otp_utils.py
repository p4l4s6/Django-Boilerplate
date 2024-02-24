import random

from django.core.exceptions import ObjectDoesNotExist

from coreapp.models import UserConfirmation


def generate_code(user):
    code = str(random.randint(100000, 999999))
    while UserConfirmation.objects.filter(confirmation_code=code, user=user).exists():
        code = str(random.randint(100000, 999999))
    return code


def create_user_confirmation(user, ip_address):
    confirmation_code = UserConfirmation.objects.create(
        user=user,
        ip_address=ip_address,
        confirmation_code=generate_code(user))
    confirmation_code.save()
    return confirmation_code


def is_code_valid(user, code):
    try:
        otp_code = get_code(user, code)
        return True
    except ObjectDoesNotExist:
        return False


def get_code(user, code):
    return UserConfirmation.objects.get(user=user, is_used=False, confirmation_code=code)


def send_otp(user_confirmation):
    pass
    # send_otp_via_sms(user_confirmation.user.mobile, user_confirmation.confirmation_code)
