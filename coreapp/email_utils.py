import threading

from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.template import Template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _


class EmailThread(threading.Thread):
    def __init__(self, msg):
        self.msg = msg
        threading.Thread.__init__(self)

    def run(self):
        self.msg.send()


def generate_template(template_content):
    return Template(template_content)


def send_email(subject, to, data, template):
    html_content = render_to_string(template, {'data': data})
    text_content = strip_tags(html_content)
    from_email = config('EMAIL_HOST_USER')
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    EmailThread(msg).start()


def send_welcome_email(email, data):
    send_email(_("Your Account is Registered"), email, data, "email/auth/welcome_email.html")


def send_forget_password_email(email, data):
    send_email(_("Please Verify Your Identity"), email, data, "email/auth/forget_password.html")


def send_account_verify_email(email, data):
    send_email(_("Please Verify Your Account"), email, data, "email/auth/verify_your_account.html")


def send_account_deactivation_email(email, data):
    send_email(_("Your Account has been deactivated"), email, data, "email/auth/account_deactivated.html")


def send_pending_approval_email(email, data):
    send_email(_("Pending for Admin Approval"), email, data, "email/auth/pending_approval.html")
