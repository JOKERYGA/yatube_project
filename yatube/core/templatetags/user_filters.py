from django import template
# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# добавляею к ним и наш фильтр.
register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})

