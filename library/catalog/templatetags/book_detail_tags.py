from catalog.models import BookInstance
from django import template

register = template.Library()


@register.simple_tag
def run_extension(bookInstance: BookInstance, counter):
    """Show the book instance ID and its position in the list."""
    return f"{bookInstance.id} is book #{counter} in this list"
