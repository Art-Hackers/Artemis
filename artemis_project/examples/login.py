"""
Shows the form validation system: Field + Form + validators.

    python examples/login.py
"""

import artemis as art

app = art.App("Sign In", theme="indigo", window_size=(360, 520))

email = art.Field("", art.validators.required(), art.validators.email())
password = art.Field("", art.validators.required(), art.validators.min_length(6))
form = art.Form(email=email, password=password)


def handle_login(values):
    app.toast(f"Welcome, {values['email']}!")


@app.page("/")
def home(page):
    return art.Column(
        [
            art.Title("Sign in"),
            art.Input(label="Email", field=email),
            art.Input(label="Password", field=password, password=True),
            art.Button("Sign in", on_click=form.submit(handle_login)),
        ],
        gap=12,
    )


if __name__ == "__main__":
    app.run()
