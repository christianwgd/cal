from django import template
register = template.Library()


@register.simple_tag
def is_default(compare, first, second):
    if first is None or len(first) == 0:
        if second == compare:
            return 'checked'
    else:
        if first == compare:
            return 'checked'
    return ''
