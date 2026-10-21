from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm
from patients.models import Patient


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif User.objects.filter(username=form.cleaned_data["username"]).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email=form.cleaned_data["email"]).exists():
                messages.error(request, "Email already exists.")
            else:
                user = form.save(commit=False)
                user.set_password(password)
                user.save()

                # UserProfile is created by post_save signal; now populate fields
                profile = user.profile
                profile.role = form.cleaned_data.get("role", "patient")
                profile.preferred_language = form.cleaned_data.get("preferred_language", "en")
                profile.phone_number = form.cleaned_data.get("phone_number", "")
                profile.assigned_center = form.cleaned_data.get("assigned_center", "")
                profile.save()

                # Set session language preference
                request.session['django_language'] = profile.preferred_language

                # If registered as a patient, create linked patient record
                if profile.role == 'patient':
                    full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                    Patient.objects.create(
                        user=user,
                        registered_by=user,
                        full_name=full_name,
                        phone_number=profile.phone_number,
                        center=profile.assigned_center,
                        consent_given=True
                    )

                # Log user in directly
                login(request, user)
                messages.success(request, f"Welcome to MediPredict AI, {user.first_name or user.username}!")

                if profile.role == 'chw':
                    return redirect("chw_portal")
                return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                if hasattr(user, 'profile') and user.profile.preferred_language:
                    request.session['django_language'] = user.profile.preferred_language

                messages.success(request, "Welcome back!")
                if hasattr(user, 'profile') and user.profile.role == 'chw':
                    return redirect("chw_portal")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


def set_language(request, lang_code):
    """
    Switches active interface language between en, hi, mr and persists in session/profile
    """
    if lang_code in ['en', 'hi', 'mr']:
        request.session['django_language'] = lang_code
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            request.user.profile.preferred_language = lang_code
            request.user.profile.save(update_fields=['preferred_language'])
    
    # Return to previous page or dashboard
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/dashboard/'
    return redirect(next_url)