from django.contrib import admin, messages

from courses.formatting import format_toman
from courses.models import Course, Order
from courses.services import send_course_access_email


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price_toman", "is_published", "created_at")
    list_filter = ("is_published",)
    list_editable = ("is_published",)
    search_fields = ("title", "short_description")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "is_published", "price", "cover")}),
        ("متن", {"fields": ("short_description", "description", "delivery_email_body")}),
        ("زمان", {"fields": ("created_at",)}),
    )

    @admin.display(description="قیمت", ordering="price")
    def price_toman(self, obj):
        return format_toman(obj.price)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "buyer_name",
        "buyer_email",
        "course",
        "amount_toman",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("buyer_name", "buyer_email", "course__title")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    actions = ("resend_delivery_email",)

    @admin.display(description="مبلغ", ordering="amount")
    def amount_toman(self, obj):
        return format_toman(obj.amount)

    @admin.action(description="ارسال دوباره ایمیل دوره")
    def resend_delivery_email(self, request, queryset):
        sent = 0
        failed = 0
        for order in queryset.select_related("course"):
            if order.status != Order.Status.PAID:
                failed += 1
                continue
            try:
                send_course_access_email(order)
            except Exception:
                failed += 1
            else:
                sent += 1
        if sent:
            self.message_user(request, f"ایمیل {sent} سفارش ارسال شد.", messages.SUCCESS)
        if failed:
            self.message_user(
                request,
                f"{failed} سفارش ارسال نشد. فقط سفارش پرداخت‌شده ایمیل می‌گیرد و خطای ارسال هم اینجا شمرده می‌شود.",
                messages.ERROR,
            )
