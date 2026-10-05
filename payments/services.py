import logging

from courses.models import Order

logger = logging.getLogger(__name__)


def simulate_payment(order) -> bool:
    """پرداخت شبیه‌سازی‌شده.

    سفارش باید از قبل با مبلغ دوره ساخته شده باشد و وضعیتش pending باشد.
    این تابع در صورت موفقیت وضعیت را paid می‌کند و True برمی‌گرداند.

    برای اتصال زرین‌پال یا آیدی‌پی همین تابع را عوض کنید:
    سفارش pending بماند، خریدار به درگاه برود، و در callback تأییدشده
    status برابر paid شود. ارسال ایمیل دوره بیرون از این تابع است.
    """
    order.status = Order.Status.PAID
    order.save(update_fields=["status"])
    logger.info("simulated payment marked order %s as paid", order.pk)
    return True
