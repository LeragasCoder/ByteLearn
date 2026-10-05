from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField("عنوان", max_length=200)
    slug = models.SlugField(
        "نامک",
        max_length=200,
        unique=True,
        help_text="فقط حروف انگلیسی، عدد و خط تیره. در نشانی صفحه استفاده می‌شود.",
    )
    short_description = models.CharField("توضیح کوتاه", max_length=300)
    description = models.TextField("توضیح کامل")
    price = models.PositiveIntegerField("قیمت (تومان)")
    cover = models.ImageField("تصویر جلد", upload_to="covers/", blank=True)
    is_published = models.BooleanField("منتشر شده", default=False)
    delivery_email_body = models.TextField(
        "متن ایمیل تحویل",
        help_text="بعد از خرید برای خریدار ایمیل می‌شود: لینک، رمز و راهنمای دسترسی.",
    )
    created_at = models.DateTimeField("زمان ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"
        ordering = ["pk"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "course"
            candidate = base
            taken = type(self).objects.all()
            if self.pk:
                taken = taken.exclude(pk=self.pk)
            number = 2
            while taken.filter(slug=candidate).exists():
                candidate = f"{base}-{number}"
                number += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        PAID = "paid", "پرداخت‌شده"
        FAILED = "failed", "ناموفق"

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="دوره",
    )
    buyer_name = models.CharField("نام خریدار", max_length=120)
    buyer_email = models.EmailField("ایمیل خریدار")
    amount = models.PositiveIntegerField("مبلغ (تومان)")
    status = models.CharField(
        "وضعیت",
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.buyer_name} — {self.course}"
