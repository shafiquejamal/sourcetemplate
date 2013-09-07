# http://stackoverflow.com/questions/3927018/django-how-to-check-if-field-widget-is-checkbox-in-the-template

from django.template import Library
register = Library()

@register.filter(name='input_type')
def input_type(field):
  return field.field.widget.__class__.__name__

#  return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__