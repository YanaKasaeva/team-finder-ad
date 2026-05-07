from urllib.parse import urlparse

from django import forms

from .constants import GITHUB_HOSTS


def validate_github_url(url):
    if not url:
        return url

    host = urlparse(url).netloc.lower()
    if host not in GITHUB_HOSTS:
        raise forms.ValidationError("Ссылка должна вести именно на GitHub")

    return url
