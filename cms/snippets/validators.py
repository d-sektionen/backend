from django.core.validators import ValidationError
import re
from functools import partial

def is_color_validator(value):
  if not len(value) in [6, 3]:
    raise ValidationError("Must be 6 or 3 characters.")
  pattern = re.compile("[A-F0-9]*")
  if not pattern.fullmatch(value.upper()):
    raise ValidationError("Must only contain 0-9 or A-F.")

def color_lightness_checker(lightness, color):
  is_color_validator(color)
  
  normalized_color = color
  if len(color) == 3:
    normalized_color = ''.join(c+c for c in color)

  red = int(normalized_color[:2], 16)
  green = int(normalized_color[2:4], 16)
  blue = int(normalized_color[4:], 16)

  calculated_lightness = red*0.299 + green*0.587 + blue*0.114

  if calculated_lightness < lightness:
    raise ValidationError("Color is too dark.")

def color_lightness_validator(lightness):
  return partial(color_lightness_checker, lightness)
