from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page


class HomePage(Page):
    hero_title = models.CharField(
        max_length=255, blank=True, default="Вы принимаете решения — мы создаём возможности",
        verbose_name="Заголовок героя",
    )
    hero_subtitle = models.CharField(
        max_length=500, blank=True,
        default="Институт Проектного Мышления — комплексное проектирование гражданских объектов капитального строительства.",
        verbose_name="Подзаголовок героя",
    )
    intro_heading = models.CharField(
        max_length=255, blank=True, default="О компании",
    )
    intro_body = RichTextField(blank=True, verbose_name="Вступительный текст")

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("hero_title"), FieldPanel("hero_subtitle")],
            heading="Герой-блок с 3D-картой",
        ),
        MultiFieldPanel(
            [FieldPanel("intro_heading"), FieldPanel("intro_body")],
            heading="О компании",
        ),
        InlinePanel("stats", label="Показатели"),
    ]

    def get_context(self, request):
        from projects.models import ProjectIndexPage, ProjectPage
        from services.models import ServicePage

        context = super().get_context(request)
        context["projects"] = (
            ProjectPage.objects.live().order_by("-year", "title").specific()
        )
        context["services"] = ServicePage.objects.live().order_by("path").specific()
        index = ProjectIndexPage.objects.live().first()
        context["portfolio_url"] = index.url if index else "#"
        return context


class HomeStat(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name="stats")
    value = models.CharField(max_length=32, verbose_name="Значение")
    label = models.CharField(max_length=120, verbose_name="Подпись")

    panels = [FieldPanel("value"), FieldPanel("label")]
