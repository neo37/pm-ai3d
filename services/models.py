from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


ICON_CHOICES = [
    ("blueprint", "Чертёж"),
    ("lightbulb", "Концепция"),
    ("building", "Здание"),
    ("frame", "Конструкции"),
    ("network", "Инженерные сети"),
    ("check", "Согласование"),
    ("shield", "Надзор"),
    ("palette", "Дизайн"),
]


class ServiceIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["services.ServicePage"]

    def get_context(self, request):
        context = super().get_context(request)
        context["services"] = (
            ServicePage.objects.child_of(self).live().order_by("path").specific()
        )
        return context


class ServicePage(Page):
    icon = models.CharField(
        max_length=20, choices=ICON_CHOICES, default="blueprint",
        verbose_name="Иконка",
    )
    summary = models.CharField(
        max_length=300, blank=True, verbose_name="Краткое описание",
    )
    body = RichTextField(blank=True, verbose_name="Полное описание")

    search_fields = Page.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("icon"),
        FieldPanel("summary"),
        FieldPanel("body"),
    ]

    parent_page_types = ["services.ServiceIndexPage"]
