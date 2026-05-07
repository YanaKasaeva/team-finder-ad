from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


PROJECTS_PER_PAGE = 12


def projects_list(request):
    projects = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    paginator = Paginator(projects, PROJECTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/project_list.html",
        {"projects": page_obj, "page_obj": page_obj},
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        id=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def favorite_projects(request):
    projects = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    paginator = Paginator(projects, PROJECTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": page_obj, "page_obj": page_obj},
    )


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return redirect("projects:detail", project_id=project.id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@require_POST
@login_required
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user.favorites.filter(id=project.id).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@require_POST
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner == request.user:
        return JsonResponse(
            {"status": "error", "message": "Автор уже участвует в проекте"}, status=400
        )

    if project.participants.filter(id=request.user.id).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    # JS из шаблона ждёт ключ participant, поэтому возвращаем именно его.
    return JsonResponse({"status": "ok", "participant": participant})


@require_POST
@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Нет прав"}, status=403)

    if project.status == Project.STATUS_OPEN:
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])

    return JsonResponse({"status": "ok", "project_status": project.status})
