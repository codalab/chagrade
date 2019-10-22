from django import template

register = template.Library()


@register.inclusion_tag('klasses/klass_header.html', takes_context=True)
def klass_header(context):
    return {
        'klass': context['klass'],
        'request': context['request'],
    }