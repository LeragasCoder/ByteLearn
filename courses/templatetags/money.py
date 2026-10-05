from django import template

from courses.formatting import format_toman

register = template.Library()


@register.filter
def toman(value):
    return format_toman(value)
