from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import ApplicationForm, ApplicationStatusForm, CompanyForm, JobForm, RegistrationForm
from .models import Application, Company, Job, Profile
from .permissions import role_required


def job_list(request):
    jobs = Job.objects.filter(is_active=True).filter(
        Q(closing_date__isnull=True) | Q(closing_date__gte=timezone.localdate())
    ).select_related("company")
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    employment_type = request.GET.get("type", "")
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(company__name__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)
    filters = request.GET.copy()
    filters.pop("page", None)
    return render(request, "jobs/job_list.html", {
        "page_obj": Paginator(jobs, 6).get_page(request.GET.get("page")),
        "query": query, "location": location, "selected_type": employment_type,
        "employment_types": Job.EmploymentType.choices, "filters": filters.urlencode(),
    })


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related("company", "company__owner"), pk=pk)
    application = None
    is_owner = request.user.is_authenticated and job.company.owner_id == request.user.pk
    if request.user.is_authenticated:
        application = Application.objects.filter(job=job, candidate=request.user).first()
    # Closed roles remain available to their owner and past applicants only.
    if not job.accepting_applications and not is_owner and not application:
        from django.http import Http404
        raise Http404("This role is no longer accepting applications.")
    return render(request, "jobs/job_detail.html", {"job": job, "application": application, "is_owner": is_owner})


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. Welcome to Launchpad!")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        return HttpResponseForbidden("This account has no portal role. Use a candidate or employer account.")
    if profile.role == Profile.Role.EMPLOYER:
        jobs = Job.objects.filter(company__owner=request.user).annotate(application_count=Count("applications"))
        return render(request, "jobs/employer_dashboard.html", {"jobs": jobs, "company": request.user.company})
    applications = Application.objects.filter(candidate=request.user).select_related("job", "job__company")
    return render(request, "jobs/candidate_dashboard.html", {"applications": applications})


@role_required(Profile.Role.EMPLOYER)
@require_http_methods(["GET", "POST"])
def company_edit(request):
    company = get_object_or_404(Company, owner=request.user)
    form = CompanyForm(request.POST or None, instance=company)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Company profile updated.")
        return redirect("dashboard")
    return render(request, "jobs/form.html", {"form": form, "title": "Company profile", "intro": "Introduce your company to candidates.", "button": "Save company"})


@role_required(Profile.Role.EMPLOYER)
@require_http_methods(["GET", "POST"])
def job_create(request):
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.company = get_object_or_404(Company, owner=request.user)
        job.save()
        messages.success(request, "Your role has been posted.")
        return redirect("job_detail", pk=job.pk)
    return render(request, "jobs/form.html", {"form": form, "title": "Post a role", "intro": "Be clear about the work, expectations and skills.", "button": "Create role"})


@role_required(Profile.Role.EMPLOYER)
@require_http_methods(["GET", "POST"])
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, company__owner=request.user)
    form = JobForm(request.POST or None, instance=job)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Role updated.")
        return redirect("dashboard")
    return render(request, "jobs/form.html", {"form": form, "title": "Edit role", "intro": "Uncheck accept applications to close this role while keeping its history.", "button": "Save changes"})


@role_required(Profile.Role.EMPLOYER)
@require_http_methods(["GET", "POST"])
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, company__owner=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Role and its applications deleted.")
        return redirect("dashboard")
    return render(request, "jobs/job_confirm_delete.html", {"job": job})


@role_required(Profile.Role.CANDIDATE)
@require_http_methods(["GET", "POST"])
def apply(request, pk):
    job = get_object_or_404(Job.objects.select_related("company"), pk=pk)
    if not job.accepting_applications:
        messages.error(request, "This role is closed for applications.")
        return redirect("dashboard")
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.info(request, "You have already applied to this role.")
        return redirect("dashboard")
    form = ApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            # The unique database constraint also catches simultaneous duplicate submissions.
            with transaction.atomic():
                application = form.save(commit=False)
                application.job = job
                application.candidate = request.user
                application.save()
        except IntegrityError:
            messages.info(request, "You have already applied to this role.")
        else:
            messages.success(request, "Application sent. Track its status in your dashboard.")
        return redirect("dashboard")
    return render(request, "jobs/apply.html", {"form": form, "job": job})


@role_required(Profile.Role.EMPLOYER)
def applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, company__owner=request.user)
    applications = job.applications.select_related("candidate")
    return render(request, "jobs/applicants.html", {"job": job, "applications": applications, "statuses": Application.Status.choices})


@role_required(Profile.Role.EMPLOYER)
@require_POST
def application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, job__company__owner=request.user)
    form = ApplicationStatusForm(request.POST, instance=application)
    if form.is_valid():
        form.save()
        messages.success(request, "Application status updated.")
    else:
        messages.error(request, "Choose a valid application status.")
    return redirect("applicants", pk=application.job_id)
