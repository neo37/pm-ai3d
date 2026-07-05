from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index


class StandardPage(Page):
    """Универсальная контентная страница (О компании, Документы, Политика)."""

    intro = models.CharField(max_length=500, blank=True, verbose_name="Подзаголовок")
    body = RichTextField(blank=True, verbose_name="Содержание")
    lead_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )

    search_fields = Page.search_fields + [index.SearchField("body")]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("lead_image"),
        FieldPanel("body"),
        InlinePanel("documents", label="Документы / изображения"),
    ]


class StandardPageAttachment(Orderable):
    page = ParentalKey(
        StandardPage, on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(max_length=255, blank=True)
    document = models.ForeignKey(
        "wagtaildocs.Document", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )

    panels = [FieldPanel("title"), FieldPanel("document"), FieldPanel("image")]


class ContactsPage(Page):
    intro = models.CharField(max_length=500, blank=True, verbose_name="Подзаголовок")
    address = models.CharField(max_length=255, blank=True, verbose_name="Адрес")
    legal_address = models.CharField(
        max_length=255, blank=True, verbose_name="Юридический адрес"
    )
    phones = models.CharField(max_length=255, blank=True, verbose_name="Телефоны")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    latitude = models.FloatField(default=55.783347, verbose_name="Широта")
    longitude = models.FloatField(default=37.572549, verbose_name="Долгота")
    body = RichTextField(blank=True, verbose_name="Дополнительно")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("address"),
                FieldPanel("legal_address"),
                FieldPanel("phones"),
                FieldPanel("email"),
            ],
            heading="Контактные данные",
        ),
        MultiFieldPanel(
            [FieldPanel("latitude"), FieldPanel("longitude")],
            heading="Карта",
        ),
        FieldPanel("body"),
    ]
