from urllib.parse import urlparse

from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "status": forms.Select(
                choices=[
                    (Project.STATUS_OPEN, "Открыт"),
                    (Project.STATUS_CLOSED, "Закрыт"),
                ]
            )
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if not url:
            return url
        host = urlparse(url).netloc.lower()
        if host not in {"github.com", "www.github.com"}:
            raise forms.ValidationError("Ссылка должна вести именно на GitHub")
        return url
