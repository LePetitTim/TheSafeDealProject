from django import template
from django.template.defaultfilters import stringfilter
from TheSafeDeal_NoAdmin.functions import *

register = template.Library()

@register.filter
@stringfilter
def name2email(value):
    return get_name_from_email(value)