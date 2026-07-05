from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index


CATEGORY_CHOICES = [
    ("residential", "Жилые комплексы"),
    ("public", "Общественные здания"),
    ("cottage", "Коттеджи, интерьеры и мебель"),
    ("planning", "Проекты планировки и градостроительство"),
    ("design", "Дизайн-проекты"),
]

CATEGORY_COLORS = {
    "residential": "#e0a458",
    "public": "#5b8def",
    "cottage": "#57b894",
    "planning": "#a68bd6",
    "design": "#e0685a",
}


class ProjectIndexPage(Page):
    """Портфолио — каталог объектов и 3D-карта облёта."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["projects.ProjectPage"]

    def get_projects(self):
        return (
            ProjectPage.objects.child_of(self)
            .live()
            .order_by("-year", "title")
            .specific()
        )

    def get_context(self, request):
        context = super().get_context(request)
        context["projects"] = self.get_projects()
        context["categories"] = CATEGORY_CHOICES
        return context


class ProjectPage(Page):
    """Один объект/проект компании."""

    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="residential",
        verbose_name="Категория",
    )
    summary = models.CharField(
        max_length=255, blank=True, verbose_name="Краткое описание",
    )
    body = RichTextField(blank=True, verbose_name="Описание")

    address = models.CharField(
        max_length=255, blank=True, verbose_name="Адрес",
        help_text="Например: Москва, Крылатские Холмы",
    )
    latitude = models.FloatField(
        default=55.751244, verbose_name="Широта",
        help_text="Координата для 3D-карты",
    )
    longitude = models.FloatField(
        default=37.618423, verbose_name="Долгота",
    )
    approximate_location = models.BooleanField(
        default=False, verbose_name="Координата приблизительная",
    )

    year = models.CharField(max_length=32, blank=True, verbose_name="Год")
    stage = models.CharField(
        max_length=64, blank=True, verbose_name="Стадия",
        help_text="Например: П, РД, ЭП",
    )
    customer = models.CharField(
        max_length=128, blank=True, verbose_name="Заказчик / застройщик",
    )

    lead_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name="Главное изображение",
    )

    search_fields = Page.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
        index.SearchField("address"),
        index.FilterField("category"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        FieldPanel("lead_image"),
        FieldPanel("summary"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("year"),
                FieldPanel("stage"),
                FieldPanel("customer"),
            ],
            heading="Параметры проекта",
        ),
        MultiFieldPanel(
            [
                FieldPanel("address"),
                FieldPanel("latitude"),
                FieldPanel("longitude"),
                FieldPanel("approximate_location"),
            ],
            heading="Расположение на карте",
        ),
        InlinePanel("gallery_images", label="Галерея"),
    ]

    parent_page_types = ["projects.ProjectIndexPage"]

    @property
    def category_label(self):
        return dict(CATEGORY_CHOICES).get(self.category, "")

    @property
    def category_color(self):
        return CATEGORY_COLORS.get(self.category, "#e0a458")

    def map_feature(self):
        """Данные объекта для MapLibre."""
        img = None
        if self.lead_image:
            img = self.lead_image.get_rendition("fill-320x220").url
        return {
            "id": self.pk,
            "title": self.title,
            "category": self.category,
            "categoryLabel": self.category_label,
            "color": self.category_color,
            "address": self.address,
            "year": self.year,
            "lng": self.longitude,
            "lat": self.latitude,
            "url": self.url,
            "image": img,
            "approximate": self.approximate_location,
        }


class ProjectGalleryImage(Orderable):
    page = ParentalKey(
        ProjectPage, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )
    caption = models.CharField(max_length=255, blank=True)

    panels = [FieldPanel("image"), FieldPanel("caption")]
