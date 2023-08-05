from django import template

from page.models import Page, MENU_TOP, MENU_BOTTOM

register = template.Library()

@register.inclusion_tag('includes/top_menu.html', takes_context=True)
def top_menu(context):
    """
    Adds published top menu pages to top menu
    """
    request = context['request']
    pages = Page.objects.published(request.user).filter(menu=MENU_TOP)

    return {
        'pages': pages,
        'path' : request.path
    }


@register.inclusion_tag('includes/bottom_menu.html', takes_context=True)
def bottom_menu(context):
    """
    Adds published top menu pages to top menu
    """
    request = context['request']
    pages = Page.objects.published(request.user).filter(menu=MENU_BOTTOM)

    return {
        'pages': pages,
        'path' : request.path
    }
