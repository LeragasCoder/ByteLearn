from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from courses import views

admin.site.site_header = "مدیریت درس‌خانه"
admin.site.site_title = "درس‌خانه"
admin.site.index_title = "دوره‌ها و سفارش‌ها"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.course_list, name="course_list"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path(
        "checkout/success/<int:order_id>/",
        views.checkout_success,
        name="checkout_success",
    ),
    path("about/", views.about, name="about"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
