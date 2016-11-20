from django.template import Library
register = Library()

@register.filter
def repeat_until(value):
    return range(value)

@register.filter
def sum_unity(value):
	return value + 1