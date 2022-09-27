import base64
import hashlib
import hmac
import logging

import requests
from decouple import config
from rest_framework import status
from django.conf import settings

from utility.models import GlobalSettings
from ..models import Payment

BILLPLZ_SERVER = "https://www.billplz-sandbox.com/api/v3"

logger = logging.getLogger('django')


def get_encode_key(global_settings):
    return base64.b64encode(f"{global_settings.billplz_token}:".encode()).decode('utf-8')


def get_settings():
    return GlobalSettings.objects.first()


def get_redirect_url():
    return f"{settings.MEDIA_HOST}/utility/payment/billplz/redirect/"


def get_callback_url():
    return f"{settings.MEDIA_HOST}/utility/payment/billplz/callback/"


# BillPlz
def create_bill(donation):
    global_settings = get_settings()
    payload = {
        'collection_id': global_settings.billplz_collection,
        'email': 'anonymous@emenem.tech',
        'name': f"Donation  for {global_settings.site_name}",
        'amount': donation.amount * 100,
        'callback_url': get_callback_url(),
        'redirect_url': get_redirect_url(),
        'description': f"Donation {donation.amount} RM for {global_settings.site_name}",
        'reference_1_label': 'uid',
        'reference_1': donation.uid,
        'reference_2_label': 'Donation To',
        'reference_2': f"{global_settings.site_name}",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {get_encode_key(global_settings)}"
    }
    r = requests.post(url=f"{BILLPLZ_SERVER}/bills", data=payload, headers=headers)
    try:
        if r.status_code == status.HTTP_200_OK:
            response = r.json()
            bill_id = response['id']
            bill_url = response['url']
            donation.bill_uid = bill_id
            donation.bill_url = bill_url
            donation.save()
            return bill_url
    except KeyError:
        logger.error(r.json())
    return None


def generate_signature(d):
    d.pop('billplz[x_signature]')
    l = []
    for k, v in d.items():
        l.append(f'billplz{k[8:-1]}' + f'{v[0]}')
    source_string = '|'.join(sorted(l))
    return hmac.new(get_settings().billplz_signature.encode(), source_string.encode(), hashlib.sha256).hexdigest()


def verify_billplz_request(x_signature, d):
    return generate_signature(d) == x_signature
