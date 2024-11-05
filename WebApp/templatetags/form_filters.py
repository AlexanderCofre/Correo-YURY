from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    # Verificar si el campo tiene el método as_widget, que indica que es un campo de formulario
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    # Si no es un campo de formulario, simplemente devuelve el valor original
    return field

