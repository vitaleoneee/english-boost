from django import template

register = template.Library()


@register.filter
def pluralize_ru(count, forms):
    """
    Declines a word by number in Russian.
    """
    one, few, many = forms.split(',')
    if 11 <= (count % 100) <= 14:
        return many
    elif count % 10 == 1:
        return one
    elif 2 <= count % 10 <= 4:
        return few
    else:
        return many


@register.filter(name='gettype')
def gettype(value):
    return type(value).__name__
