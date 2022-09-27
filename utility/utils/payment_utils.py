from utility import constants
from utility.utils import billplz_utils, paypal_utils


def generate_bill_url(payment):
    if payment.payment_method == constants.PaymentMethod.BILLPLZ:
        return billplz_utils.create_bill(payment)
    else:
        return paypal_utils.create_payment(payment)