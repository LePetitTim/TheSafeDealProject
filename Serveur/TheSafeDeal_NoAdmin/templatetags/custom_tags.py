from django import template
register = template.Library()

@register.filter()
def to_month(value):
    tabMonth = ["Jan","Fev","Mar","Avr","Mai","Juin","Juil","Aou","Sep",'Oct','Nov',"Dec"]
    return tabMonth[value-1]

@register.filter()
def replace_colour(value):
	if value=='R':
		return "#FF0000"
	elif value=='V':
		return "#00FF00"
	elif value=="O":
		return "#FF8C00"
	else:
		return "#FFFFFF"
@register.filter
def get_item(dictionary):
    return next(iter(dictionary))


