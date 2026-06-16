from django.core.mail import send_mail
from django.conf import settings

def send_verification_mail(user, subject, message) :
    send_mail(
        recipient_list=[user],
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        fail_silently=False
    )

