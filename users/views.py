from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.constants import USERS_PER_PAGE
from team_finder.services import paginate_queryset

from .forms import LoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import User


def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)

        return redirect("projects:list")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)

    if form.is_valid():
        login(request, form.cleaned_data["user"])

        return redirect("projects:list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)

    return redirect("projects:list")


def user_detail(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects"),
        id=user_id,
    )

    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if form.is_valid():
        form.save()

        return redirect("users:detail", user_id=request.user.id)

    return render(
        request,
        "users/edit_profile.html",
        {"form": form, "user": request.user},
    )


@login_required
def change_password(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)

        return redirect("users:detail", user_id=request.user.id)

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

    page_obj = paginate_queryset(request, participants, USERS_PER_PAGE)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "active_filter": active_filter,
        },
    )
