import logging

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from utility.constants import PaymentStatus
from utility.models import GlobalSettings, Payment

logger = logging.getLogger('django')
SERVER_URL = "https://api-m.sandbox.paypal.com"


def get_settings():
    return GlobalSettings.objects.first()


def get_access_token():
    global_settings = get_settings()
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    payload = {"grant_type": "client_credentials"}
    response = requests.post(
        f"{SERVER_URL}/v1/oauth2/token",
        data=payload,
        headers=headers,
        auth=(global_settings.paypal_client_id, global_settings.paypal_client_secret),
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


def create_payment(payment):
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {"currency_code": "USD", "value": f"{payment.amount}"},
                "reference_id": str(payment.uid),
            }
        ],
        "application_context": {
            "return_url": f"{settings.MEDIA_HOST}/utility/payment/paypal/status/success/",
            "cancel_url": f"{settings.MEDIA_HOST}/utility/payment/paypal/status/cancel/",
        },
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_access_token()}",
    }
    response = requests.post(
        f"{SERVER_URL}/v2/checkout/orders", json=payload, headers=headers
    )
    if response.status_code == 201 or response.status_code == 200:
        data = response.json()
        links = data["links"]
        for link in links:
            if link["rel"] == "approve":
                bill_uid = data["id"]
                bill_url = link["href"]
                payment.bill_url = bill_url
                payment.bill_uid = bill_uid
                payment.save()
                return bill_url
    return None


def verify_paypal_signature(data):
    return True


def process_payment(data):
    payment_id = data["resource"]["id"]
    try:
        payment = Payment.objects.get(bill_uid=payment_id)
        payment.status = PaymentStatus.SUCCESS
        payment.save()
    except ObjectDoesNotExist:
        logger.error("Payment verification failed")
