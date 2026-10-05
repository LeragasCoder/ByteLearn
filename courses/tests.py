from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from courses.models import Course, Order


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class StoreFlowTests(TestCase):
    def setUp(self):
        self.course = Course.objects.get(slug="python-daily-work")

    def test_home_lists_published_courses_and_prices(self):
        response = self.client.get(reverse("course_list"))
        self.assertContains(response, "پایتون برای کار روزمره")
        self.assertContains(response, "جنگو از مدل تا صفحهٔ خرید")
        self.assertContains(response, "امنیت شبکه برای تیم‌های کوچک")
        self.assertContains(response, "اکسل برای تحلیل داده")
        self.assertContains(response, "لینوکس سرور، از نصب تا استقرار")
        self.assertContains(response, "۱٬۴۹۰٬۰۰۰ تومان")
        self.assertContains(response, "dir=\"rtl\"")

    def test_invalid_email_is_persian_and_creates_no_order(self):
        response = self.client.post(
            self.course.get_absolute_url(),
            {"buyer_name": "سارا محمدی", "buyer_email": "not-an-email"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ایمیل واردشده معتبر نیست.")
        self.assertEqual(Order.objects.count(), 0)

    def test_missing_name_is_persian(self):
        response = self.client.post(
            self.course.get_absolute_url(),
            {"buyer_name": " ", "buyer_email": "sara@example.com"},
        )
        self.assertContains(response, "نام را وارد کنید.")
        self.assertEqual(Order.objects.count(), 0)

    def test_purchase_marks_paid_and_sends_course_email(self):
        response = self.client.post(
            self.course.get_absolute_url(),
            {"buyer_name": "  سارا   محمدی ", "buyer_email": "Sara@Example.com"},
            follow=True,
        )
        order = Order.objects.get()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.amount, self.course.price)
        self.assertEqual(order.buyer_name, "سارا محمدی")
        self.assertEqual(order.buyer_email, "sara@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"دسترسی به دوره: {self.course.title}")
        self.assertEqual(mail.outbox[0].body, self.course.delivery_email_body)
        self.assertEqual(mail.outbox[0].to, ["sara@example.com"])
        self.assertContains(response, "خرید ثبت شد. اطلاعات دوره به ایمیل شما ارسال می‌شود.")
        self.assertContains(response, self.course.title)
        self.assertContains(response, "sara@example.com")
        self.assertNotContains(response, "PY-4821-KHANE")

    def test_email_failure_keeps_paid_order(self):
        with patch("courses.views.send_course_access_email", side_effect=OSError("down")):
            response = self.client.post(
                self.course.get_absolute_url(),
                {"buyer_name": "سارا محمدی", "buyer_email": "sara@example.com"},
                follow=True,
            )
        order = Order.objects.get()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertContains(response, "ارسال ایمیل در این لحظه انجام نشد")
        self.assertContains(response, "سفارش شما محفوظ است")

    def test_failed_payment_does_not_email(self):
        def fail(order):
            order.status = Order.Status.FAILED
            order.save(update_fields=["status"])
            return False

        with patch("courses.views.simulate_payment", side_effect=fail):
            response = self.client.post(
                self.course.get_absolute_url(),
                {"buyer_name": "سارا محمدی", "buyer_email": "sara@example.com"},
            )
        self.assertContains(response, "ثبت خرید انجام نشد")
        self.assertEqual(Order.objects.get().status, Order.Status.FAILED)
        self.assertEqual(len(mail.outbox), 0)

    def test_unpublished_course_is_hidden(self):
        self.course.is_published = False
        self.course.save()
        self.assertNotContains(self.client.get(reverse("course_list")), self.course.title)
        self.assertEqual(self.client.get(self.course.get_absolute_url()).status_code, 404)

    def test_admin_can_resend_email(self):
        self.client.post(
            self.course.get_absolute_url(),
            {"buyer_name": "سارا محمدی", "buyer_email": "sara@example.com"},
        )
        order = Order.objects.get()
        mail.outbox.clear()
        user = get_user_model().objects.create_superuser("root", "root@example.com", "pass12345x")
        self.client.force_login(user)
        response = self.client.post(
            reverse("admin:courses_order_changelist"),
            {"action": "resend_delivery_email", "_selected_action": [str(order.pk)]},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"دسترسی به دوره: {self.course.title}")
