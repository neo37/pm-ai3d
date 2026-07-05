from django import template
from wagtail.models import Page, Site

register = template.Library()


def _site_root(context):
    request = context.get("request")
    if request is not None:
        try:
            return Site.find_for_request(request).root_page
        except (AttributeError, Site.DoesNotExist):
            pass
    site = Site.objects.filter(is_default_site=True).first()
    return site.root_page if site else None


def _menu_items(context):
    root = _site_root(context)
    if root is None:
        return []
    return root.get_children().live().in_menu()


@register.inclusion_tag("tags/main_menu.html", takes_context=True)
def main_menu(context):
    calling_page = context.get("page")
    return {
        "menu_items": _menu_items(context),
        "request": context.get("request"),
        "calling_page": calling_page,
    }


@register.inclusion_tag("tags/footer_menu.html", takes_context=True)
def footer_menu(context):
    return {"menu_items": _menu_items(context)}


@register.simple_tag(takes_context=True)
def contacts_url(context):
    from sitepages.models import ContactsPage

    page = ContactsPage.objects.live().first()
    return page.url if page else "/contacts/"
