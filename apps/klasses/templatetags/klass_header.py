from django import template

register = template.Library()


@register.inclusion_tag('klasses/klass_header.html')
def klass_header(klass):
    return {'klass': klass}