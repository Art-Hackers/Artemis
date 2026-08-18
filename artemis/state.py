"""
State is intentionally dumb. It's just a box holding a value so you have
something to mutate from inside a click handler (Python closures can't
reassign a plain local variable from a nested function without `nonlocal`
everywhere, which gets ugly fast).

    count = art.State(0)

    def add(e):
        count.value += 1

Discrete controls (Button, Switch, Slider, Checkbox, Dropdown) trigger a
full page re-render on their own after your handler runs, so you almost
never have to think about updating the screen yourself - just change the
value and the redraw happens for you.

Text inputs are the one exception - see Input()'s `bind` argument in
widgets.py for why.
"""


class State:
    def __init__(self, value):
        self._value = value
        self._listeners = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        for fn in self._listeners:
            fn(new_value)

    def set(self, new_value):
        """Same as `.value = x` but usable directly as a lambda target, e.g.
        on_click=lambda e: count.set(count.value + 1)"""
        self.value = new_value
        return new_value

    def toggle(self):
        """Handy shortcut for boolean state."""
        self.value = not self._value
        return self._value

    def __repr__(self):
        return f"State({self._value!r})"
