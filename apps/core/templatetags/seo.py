import json

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

_ESCAPES = {ord(">"): "\\u003E", ord("<"): "\\u003C", ord("&"): "\\u0026"}


@register.simple_tag
def jsonld(data):
    """Render a JSON-LD script block with HTML-significant characters escaped."""
    payload = json.dumps(data, ensure_ascii=False).translate(_ESCAPES)
    return format_html('<script type="application/ld+json">{}</script>', mark_safe(payload))
