import re

from django.core.exceptions import ValidationError


def phone_validate(value):
    PHONE_REGEX = '^\d{3}-\d{3,4}-\d{4}$'
    if not re.match(PHONE_REGEX, value):
        raise ValidationError('INVALID_PHONE_NUMBER')


def password_validate(value):
    PASSWORD_REGEX = '^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$'
    if not re.match(PASSWORD_REGEX, value):
        raise ValidationError('INVALID_PASSWORD')
