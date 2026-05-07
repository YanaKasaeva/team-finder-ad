from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import User


USERS_PER_PAGE = 12


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("projects:list")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects"), id=user_id
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = ProfileForm(instance=request.user)
    return render(
        request, "users/edit_profile.html", {"form": form, "user": request.user}
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def users_list(request):
    participants = User.objects.all().order_by("-id")
    active_filter = request.GET.get("filter")

    if active_filter and request.user.is_authenticated:
        current_user = request.user

        if active_filter == "owners-of-favorite-projects":
            participants = User.objects.filter(
                owned_projects__in=current_user.favorites.all()
            ).distinct()

        elif active_filter == "owners-of-participating-projects":
            participants = User.objects.filter(
                owned_projects__in=current_user.participated_projects.all()
            ).distinct()

        elif active_filter == "interested-in-my-projects":
            participants = User.objects.filter(
                favorites__in=current_user.owned_projects.all()
            ).distinct()

        elif active_filter == "participants-of-my-projects":
            participants = (
                User.objects.filter(
                    participated_projects__in=current_user.owned_projects.all()
                )
                .exclude(id=current_user.id)
                .distinct()
            )

    paginator = Paginator(participants, USERS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "active_filter": active_filter,
        },
    )
