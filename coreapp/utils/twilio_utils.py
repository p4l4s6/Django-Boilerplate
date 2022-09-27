from twilio.rest import Client

from utility.models import GlobalSettings


def get_system_settings():
    global_settings = GlobalSettings.objects.first()
    return global_settings


def get_twilio_client(account_id, token):
    return Client(username=account_id, password=token)


def send_otp_via_sms(number, code):
    global_settings = get_system_settings()
    twilio_client = get_twilio_client(global_settings.twillio_account, global_settings.twillio_token)
    messages = twilio_client.messages.create(
        to=f"{number}", from_=global_settings.twillio_number, body=f"Your {global_settings.site_name} OTP is {code}"
    )
    return messages
