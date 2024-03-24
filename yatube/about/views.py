from django.views.generic.base import TemplateView


# Create your views here.
class AboutAuthorView(TemplateView):
    """Описывает информацию об авторе проекта."""
    template_name = "about/author.html"


class AboutTechView(TemplateView):
    """Описывает информацию о технологиях проекта"""
    template_name = "about/tech.html"
