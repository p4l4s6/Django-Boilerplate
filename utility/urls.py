from django.urls import path

from . import views

urlpatterns = [
    path("payment/billplz/redirect/", views.BillPlzRedirectView.as_view()),
    path("payment/billplz/callback/", views.BillPlzCallbackView.as_view()),
    path("payment/paypal/webhook/", views.PaypalWebhookApi.as_view()),
    path("payment/paypal/status/", views.PaypalSuccessFailApi.as_view()),
]
