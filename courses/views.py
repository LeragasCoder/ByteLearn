import logging

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from courses.forms import PurchaseForm
from courses.models import Course, Order
from courses.services import send_course_access_email
from payments.services import simulate_payment

logger = logging.getLogger(__name__)


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, "courses/list.html", {"courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    form = PurchaseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        order = Order.objects.create(
            course=course,
            buyer_name=form.cleaned_data["buyer_name"],
            buyer_email=form.cleaned_data["buyer_email"],
            amount=course.price,
            status=Order.Status.PENDING,
        )
        if not simulate_payment(order):
            if order.status == Order.Status.PENDING:
                order.status = Order.Status.FAILED
                order.save(update_fields=["status"])
            form.add_error(None, "ثبت خرید انجام نشد. لطفاً دوباره تلاش کنید.")
        else:
            email_ok = True
            try:
                send_course_access_email(order)
            except Exception:
                logger.exception("course email failed for order %s", order.pk)
                email_ok = False
            url = reverse("checkout_success", args=[order.pk])
            if not email_ok:
                url = f"{url}?email=failed"
            return redirect(url)
    return render(
        request,
        "courses/detail.html",
        {"course": course, "form": form},
    )


def checkout_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status=Order.Status.PAID)
    email_failed = request.GET.get("email") == "failed"
    console_email = settings.DEBUG and "console" in settings.EMAIL_BACKEND
    return render(
        request,
        "courses/success.html",
        {
            "order": order,
            "email_failed": email_failed,
            "console_email": console_email,
        },
    )


def about(request):
    return render(request, "pages/about.html")


def csrf_failure(request, reason=""):
    return render(request, "pages/csrf.html", status=403)
