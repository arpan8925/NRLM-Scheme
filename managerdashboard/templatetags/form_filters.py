from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key
    """
    return dictionary.get(key, '')

@register.filter
def is_list(value):
    """
    Check if a value is a list
    """
    return isinstance(value, list)
