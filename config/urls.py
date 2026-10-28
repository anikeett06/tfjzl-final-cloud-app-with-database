from django.contrib import admin
from django.urls import path, include
from onlinecourse import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("onlinecourse.urls")),
    path(
        "courses/<int:course_id>/",
        views.course_details,
        name="course_details"
    ),
]
