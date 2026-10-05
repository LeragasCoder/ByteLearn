import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_course_access_email(order):
    """متن delivery_email_body را برای خریدار می‌فرستد."""
    course = order.course
    subject = f"دسترسی به دوره: {course.title}"
    send_mail(
        subject=subject,
        message=course.delivery_email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.buyer_email],
        fail_silently=False,
    )
    if settings.EMAIL_BACKEND.endswith("console.EmailBackend"):
        # خروجی خام کنسول برای متن فارسی base64 است؛ این بلوک همان متن را خوانا چاپ می‌کند.
        print(
            "\n".join(
                [
                    "",
                    "========== ایمیل دوره ==========",
                    f"به: {order.buyer_email}",
                    f"موضوع: {subject}",
                    "",
                    course.delivery_email_body,
                    "========== پایان ایمیل ==========",
                    "",
                ]
            ),
            flush=True,
        )
    logger.info("course access email sent for order %s", order.pk)
