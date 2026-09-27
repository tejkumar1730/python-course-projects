from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from .models import Application, Company, Job, Profile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Your name")
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Profile.Role.choices)
    company_name = forms.CharField(max_length=120, required=False, help_text="Required only for employers.")

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "role", "company_name", "password1", "password2"]

    def clean(self):
        data = super().clean()
        if data.get("role") == Profile.Role.EMPLOYER and not data.get("company_name"):
            self.add_error("company_name", "Enter your company name.")
        return data

    @transaction.atomic
    def save(self):
        # One transaction prevents an account being left without its role or company.
        user = super().save()
        Profile.objects.create(user=user, role=self.cleaned_data["role"])
        if self.cleaned_data["role"] == Profile.Role.EMPLOYER:
            Company.objects.create(owner=user, name=self.cleaned_data["company_name"])
        return user


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "location", "website", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        # company is assigned from the logged-in employer; never trust a posted owner ID.
        fields = ["title", "location", "employment_type", "description", "requirements",
                  "salary_min", "salary_max", "closing_date", "is_active"]
        labels = {"salary_min": "Minimum annual salary (INR)", "salary_max": "Maximum annual salary (INR)", "is_active": "Accept applications"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
            "closing_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_closing_date(self):
        closing_date = self.cleaned_data.get("closing_date")
        # Existing expired jobs can still be edited/closed without changing their historical date.
        if closing_date and closing_date < timezone.localdate() and closing_date != self.instance.closing_date:
            raise forms.ValidationError("Choose today or a future date.")
        return closing_date


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cover_letter"]
        widgets = {"cover_letter": forms.Textarea(attrs={"rows": 7, "placeholder": "Tell the employer why this role interests you and what you are learning."})}

    def clean_cover_letter(self):
        text = self.cleaned_data["cover_letter"].strip()
        if len(text) < 30:
            raise forms.ValidationError("Write at least 30 characters about your interest in this role.")
        return text


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]
