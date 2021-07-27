from datetime import date

from django.core.exceptions import ValidationError


def validate_username_length(value):
    if len(value) < 3:
        raise ValidationError('Username length must be at least 3 chars!')


def validate_date(value):
    current_year = int(date.today().year)
    if value > current_year or value <= 0:
        raise ValidationError('Неверная дата')
