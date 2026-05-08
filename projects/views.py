from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.forms import ProjectForm
from projects.models import Project
from projects.services import get_projects_queryset
from team_finder.services import paginate_queryset


def projects_list(request):
    page_obj = paginate_queryset(request, get_projects_queryset())

    return render(
        request,
        "projects/project_list.html",
        {"projects": page_obj, "page_obj": page_obj},
    )


def project_detail(request, project_id):
    project = get_object_or_404(get_projects_queryset(), id=project_id)

    return render(request, "projects/project-details.html", {"project": project})


@login_required
def favorite_projects(request):
    page_obj = paginate_queryset(
        request,
        get_projects_queryset(request.user.favorites),
    )

    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": page_obj, "page_obj": page_obj},
    )


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)

        return redirect("projects:detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return redirect("projects:detail", project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        project = form.save()
        return redirect("projects:detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@require_POST
@login_required
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    favorited = request.user.favorites.filter(id=project.id).exists()

    if favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)

    return JsonResponse({"status": "ok", "favorited": not favorited})


@require_POST
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner == request.user:
        return JsonResponse(
            {"status": "error", "message": "Автор уже участвует в проекте"},
            status=HTTPStatus.BAD_REQUEST,
        )

    participant = project.participants.filter(id=request.user.id).exists()

    if participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not participant})


@require_POST
@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status == Project.STATUS_OPEN:
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])

    return JsonResponse({"status": "ok", "project_status": project.status})
