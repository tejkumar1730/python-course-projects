from django.urls import path
from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("accounts/register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("company/edit/", views.company_edit, name="company_edit"),
    path("jobs/new/", views.job_create, name="job_create"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    path("jobs/<int:pk>/apply/", views.apply, name="apply"),
    path("jobs/<int:pk>/applicants/", views.applicants, name="applicants"),
    path("applications/<int:pk>/status/", views.application_status, name="application_status"),
]
