import uuid

from django.db import models
from django.utils.functional import cached_property

from coreapp.base import BaseModel
from utility import constants
from .utils import slug_utils


class GlobalSettings(BaseModel):
    site_name = models.CharField(max_length=100)
    website_url = models.CharField(max_length=100)
    logo = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=150)
    short_desc = models.TextField(max_length=500)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    linkedin = models.CharField(max_length=100, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)
    youtube = models.CharField(max_length=100, null=True, blank=True)
    shipping_fee = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    vat_percentage = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    twilio_account = models.CharField(max_length=100)
    twilio_token = models.CharField(max_length=100)
    twilio_number = models.CharField(max_length=100)
    billplz_token = models.CharField(max_length=100)
    billplz_signature = models.CharField(max_length=100)
    billplz_collection = models.CharField(max_length=100)
    paypal_client_id = models.CharField(max_length=100)
    paypal_client_secret = models.CharField(max_length=100)

    @cached_property
    def get_logo_url(self):
        return self.logo.get_url

    def __str__(self):
        return self.site_name


class Page(BaseModel):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    slug = models.CharField(max_length=100, unique=True, db_index=True, editable=False)
    thumbnail = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="page_thumbnail")
    attachment = models.ForeignKey(
        "coreapp.Document", on_delete=models.CASCADE,
        related_name="page_attachment", null=True, blank=True
    )
    video_url = models.CharField(max_length=100, null=True, blank=True)
    page_type = models.IntegerField(choices=constants.PageType.choices)
    is_active = models.BooleanField(default=0)

    def __str__(self):
        return self.title

    @cached_property
    def get_thumbnail_url(self):
        return self.thumbnail.get_url

    @cached_property
    def get_attachment_url(self):
        return self.attachment.get_url

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_utils.generate_unique_slug(self.title, self)
        super(Page, self).save(**kwargs)


class Payment(BaseModel):
    uid = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False)
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    ip_address = models.CharField(max_length=100)
    status = models.SmallIntegerField(
        choices=constants.PaymentStatus.choices,
        default=constants.PaymentStatus.PENDING
    )
    payment_method = models.SmallIntegerField(choices=constants.PaymentMethod.choices)
    bill_uid = models.CharField(max_length=100, null=True, blank=True)
    bill_url = models.TextField()

    def __str__(self):
        return self.bill_uid
