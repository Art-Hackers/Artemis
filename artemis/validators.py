"""
Each of these is a factory - call it to get a checker function that
takes a value and returns an error message (or None if it's fine). That's
the shape `Field()` expects, and it's also easy to write your own:

    def even_number(message="Must be an even number"):
        def check(value):
            return None if int(value or 0) % 2 == 0 else message
        return check
"""

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def required(message="This field is required"):
    def check(value):
        return None if str(value or "").strip() else message
    return check


def email(message="Enter a valid email address"):
    def check(value):
        return None if _EMAIL_RE.match(str(value or "")) else message
    return check


def min_length(n, message=None):
    def check(value):
        if len(str(value or "")) < n:
            return message or f"Must be at least {n} characters"
        return None
    return check


def max_length(n, message=None):
    def check(value):
        if len(str(value or "")) > n:
            return message or f"Must be {n} characters or fewer"
        return None
    return check


def matches(other_field, message="Fields don't match"):
    """For "confirm password" style fields - pass the *other* Field object."""
    def check(value):
        return None if value == other_field.value else message
    return check


def number(message="Must be a number"):
    def check(value):
        try:
            float(value)
            return None
        except (TypeError, ValueError):
            return message
    return check
