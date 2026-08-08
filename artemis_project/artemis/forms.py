"""
Validating a login/signup form in raw Flet means manually tracking error
strings per field, wiring on_blur, and remembering not to show "required"
errors before the user's even typed anything. This is that, done once:

    email = art.Field("", art.validators.required(), art.validators.email())
    password = art.Field("", art.validators.required(), art.validators.min_length(6))
    form = art.Form(email=email, password=password)

    art.Input(label="Email", field=email)
    art.Input(label="Password", field=password, password=True)
    art.Button("Sign in", on_click=form.submit(handle_login))

`handle_login` only runs if every field passes; otherwise each Input
shows its own error and nothing else happens. Errors stay hidden until a
field's been touched (blurred, or a submit was attempted), so a fresh
form doesn't greet the user with a wall of red text.
"""

from .state import State


class Field:
    def __init__(self, value="", *validators):
        self.state = State(value)
        self.validators = validators
        self.touched = False

    @property
    def value(self):
        return self.state.value

    @value.setter
    def value(self, new_value):
        self.state.value = new_value

    @property
    def error(self):
        if not self.touched:
            return None
        for check in self.validators:
            message = check(self.state.value)
            if message:
                return message
        return None

    def touch(self):
        self.touched = True

    def is_valid(self):
        return not any(check(self.state.value) for check in self.validators)


class Form:
    def __init__(self, **fields):
        self.fields = fields

    def is_valid(self):
        for field in self.fields.values():
            field.touch()
        return all(field.is_valid() for field in self.fields.values())

    def submit(self, on_valid):
        """Returns an on_click-ready handler: touches every field (so
        errors become visible), and only calls `on_valid(values)` - a
        plain dict of field name -> value - if everything passes."""
        def handler(e):
            if self.is_valid():
                on_valid({name: field.value for name, field in self.fields.items()})
        return handler
