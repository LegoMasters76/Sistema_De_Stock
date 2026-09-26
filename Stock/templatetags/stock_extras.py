import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "em",
    "h2",
    "h3",
    "h4",
    "li",
    "ol",
    "p",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}
ALLOWED_ATTRIBUTES = {
    "a": ["href", "rel", "target"],
}
ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


@register.filter
def sanitize_html(value):
    if not value:
        return ""
    cleaned = bleach.clean(
        str(value),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True,
    )
    return mark_safe(cleaned)
