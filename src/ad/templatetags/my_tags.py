from django import template
from ad import models
register = template.Library()

@register.filter
def range_list(current, length):
    if current > 1 and current < length:
        return range(current-1, current+2)
    if length < 3:
        return range(1,length+1)
    if current == 1:
        return range(1,current+3)
    
    return range(current-2,current+1)

@register.filter
def moreB(current):
    return current-1 > 1

@register.filter
def moreF(current, length):
    return current+1 < length

@register.filter
def nocomma(i, length):
    return i < len(length)

@register.filter
def bookcount(category):
    return models.Book.objects.all().filter(category = category).count()
    