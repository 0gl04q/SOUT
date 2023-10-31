from django import template

register = template.Library()


@register.filter(name='get_by_key')
def get_by_key(dictionary: dict, key: str) -> list:
    return dictionary.get(key, '')
