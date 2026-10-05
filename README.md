# بایت لرن - ByteLearn

فروشگاه سادهٔ دوره با جنگو. خرید فعلاً شبیه‌سازی می‌شود و اطلاعات دسترسی دوره با ایمیل برای خریدار فرستاده می‌شود.

رابط فارسی و راست‌به‌چپ است. پایگاه توسعه SQLite است. پنل مدیریت جنگو برای دوره‌ها و سفارش‌ها استفاده می‌شود.

## نصب روی مک

پایتون ۳.۱۲ یا جدیدتر لازم است. اگر `python3` نصب نیست، از [python.org](https://www.python.org/downloads/) یا Homebrew (`brew install python`) بگیرید.

```bash
cd dars-khane
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py ensure_demo_admin
python manage.py runserver
```

بعد در مرورگر باز کنید: <http://127.0.0.1:8000/>

`migrate` جدول‌ها و پنج دورهٔ نمونه را می‌سازد: پایتون، جنگو، امنیت شبکه، اکسل، لینوکس.

ورود آزمایشی پنل: نام کاربری `admin` و رمز `DarsKhane-1404`. نشانی پنل: <http://127.0.0.1:8000/admin/>.

برای ساختن مدیر با رمز دلخواه، به‌جای `ensure_demo_admin` بزنید:

```bash
python manage.py createsuperuser
```

## پرداخت شبیه‌سازی‌شده

منطق پرداخت در [`payments/services.py`](payments/services.py) و تابع `simulate_payment(order)` است. این تابع سفارش را مستقیم `paid` می‌کند و درگاه، کارت بانکی یا callback ندارد.

ویو اول سفارش را با وضعیت `pending` و مبلغ برابر قیمت دوره می‌سازد، بعد همین تابع را صدا می‌زند. برای زرین‌پال یا آیدی‌پی فقط بدنهٔ `simulate_payment` (و در صورت نیاز مسیر بازگشت از درگاه) عوض می‌شود. ارسال ایمیل بیرون از لایهٔ پرداخت است و در `courses/services.py` مانده.

## ایمیل

پیش‌فرض توسعه:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

متن ایمیل، از جمله لینک و رمز دوره، در همان ترمینالی چاپ می‌شود که `runserver` را اجرا کرده. موضوع ایمیل این است: `دسترسی به دوره: {عنوان}`. بدنه از فیلد «متن ایمیل تحویل» هر دوره می‌آید.

اگر ارسال خطا بدهد، سفارشِ پرداخت‌شده حفظ می‌شود و صفحهٔ موفقیت به‌جای پیام ارسال، می‌گوید ایمیل در این لحظه نرفته است.

برای SMTP واقعی، بدون تغییر کد، این متغیرهای محیطی را بگذارید:

```bash
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export EMAIL_HOST="smtp.example.com"
export EMAIL_PORT="587"
export EMAIL_HOST_USER="you@example.com"
export EMAIL_HOST_PASSWORD="secret"
export EMAIL_USE_TLS="true"
export DEFAULT_FROM_EMAIL="درس‌خانه <you@example.com>"
```

## ادمین

- ثبت، ویرایش و انتشار دوره (تیک «منتشر شده»)
- دیدن سفارش‌ها: نام، ایمیل، دوره، مبلغ، وضعیت، زمان
- اقدام «ارسال دوباره ایمیل دوره» روی سفارش‌های پرداخت‌شده
