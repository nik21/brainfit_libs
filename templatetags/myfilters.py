import re
from django import template
from django.core.urlresolvers import reverse
from django.forms import ImageField, Textarea, CharField

register = template.Library()


@register.filter
def paragraphs(value):
    """
    Turns paragraphs delineated with newline characters into
    paragraphs wrapped in <p> and </p> HTML tags.
    https://djangosnippets.org/snippets/143/
    """
    paras = re.split(r'[\r\n]+', value)
    paras = ['<p>%s</p>' % p.strip() for p in paras]
    return '\n'.join(paras)


@register.filter(name='field_without_label', is_safe=True)
def field_without_label(value, arg):
    attrs = {'class': 'form-control'}
    if hasattr(value, 'label') and value.label:
        attrs['placeholder'] = value.label

    # Установим значение по-умолчанию
    if hasattr(value, 'data') and value.data is not None:
        attrs['value'] = value.data

    # Большие поля превращаются в textarea
    if isinstance(value.field, CharField) and isinstance(value.field.max_length, int)\
            and value.field.max_length >= 1024:
        value.field.widget = Textarea(attrs={'cols': 80, 'rows': 5})

    # Для изображений не будем показывать "current" и ссылку, а просто поле для файла
    if isinstance(value.field, ImageField):
        value.field.widget.template_with_initial = '%(input)s'

    return value.as_widget(attrs=attrs)


@register.filter(name='field_with_label', is_safe=True)
def field_with_label(value, arg):
    attrs = {'class': 'form-control'}
    if hasattr(value, 'help_text') and value.help_text:
        attrs['placeholder'] = value.help_text

    # Установим значение по-умолчанию
    if hasattr(value, 'data') and value.data is not None:
        attrs['value'] = value.data

    # Большие поля превращаются в textarea
    if isinstance(value.field, CharField) and isinstance(value.field.max_length, int)\
            and value.field.max_length >= 1024:
        value.field.widget = Textarea(attrs={'cols': 80, 'rows': 5})

    # Для изображений не будем показывать "current" и ссылку, а просто поле для файла
    if isinstance(value.field, ImageField):
        value.field.widget.template_with_initial = '%(input)s'

    return value.as_widget(attrs=attrs)


@register.simple_tag
def real_filed_name(form, key_name, *args):
    return form.fields[key_name].label if form and hasattr(form, 'fields') else key_name


@register.filter(name='add_placeholder')
def add_placeholder(value, arg):
    return value.as_widget(attrs={'placeholder': arg})


@register.simple_tag
def active(request, pattern):
    url_by_pattern = reverse(pattern)

    import re
    if re.search(url_by_pattern, request.path):
        return 'id="current"'
    return ''


@register.filter
def pluralize_ru(value, arg="товар,товара,товаров"):
    args = arg.split(",")
    if not value:
        return args[2]

    number = abs(int(value))
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return args[0]
    elif (a > 1) and (a < 5) and ((b < 10) or (b > 20)):
        return args[1]
    else:
        return args[2]
