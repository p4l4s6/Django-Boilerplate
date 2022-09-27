import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views import View
from rest_framework import status

from .api.admin.serializers import PaymentSerializer
from .constants import PaymentStatus
from .models import Payment
from .utils import billplz_utils
from .utils import paypal_utils

logger = logging.getLogger('django')


class BillPlzRedirectView(View):

    def get(self, request):
        x_signature = request.GET.get('billplz[x_signature]')
        if billplz_utils.verify_billplz_request(x_signature, dict(request.GET)):
            bill_code = request.GET.get('billplz[id]')
            is_paid = request.GET.get('billplz[paid]')
            if is_paid == 'true':
                payment = Payment.objects.get(bill_uid=bill_code)
                try:
                    payment.status = PaymentStatus.SUCCESS
                    payment.save()
                    serializer = PaymentSerializer(payment)
                    return JsonResponse({
                        "status": "success",
                        "code": 200,
                        "data": serializer.data,
                        "message": "Payment Completed Successfully",
                    })
                except ObjectDoesNotExist:
                    logger.error("Spam request identified")
        return JsonResponse({
            "status": "error",
            "code": 400,
            "data": "",
            "message": "Payment Failed",
        }, status=status.HTTP_400_BAD_REQUEST)


class BillPlzCallbackView(View):
    def get(self, request):
        return JsonResponse({
            "status": "success",
            "code": 200,
            "data": "success",
            "message": "Payment Completed Successfully in call back",
        })


class PaypalWebhookApi(View):

    def post(self, request):
        data = request.POST
        if data.POST.get("event_type") == "CHECKOUT.ORDER.APPROVED":
            paypal_utils.process_payment(data)
        return JsonResponse({}, status=status.HTTP_200_OK)


class PaypalSuccessFailApi(View):

    def get(self, request):
        paypal_status = request.GET.get("paypal_status", False)
        return JsonResponse({"status": status.HTTP_200_OK, "msg": paypal_status})
