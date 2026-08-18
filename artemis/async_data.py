"""
Every screen that loads data from somewhere ends up needing the same
three things: a loading flag, an error slot, and a value slot - and
since Artemis re-runs your page function on every click anywhere in the
app (see the README's "mental model" section), you also have to make
sure you don't accidentally re-fetch on every single one of those
re-renders. AsyncData handles all of that:

    products = art.AsyncData(lambda: art.fetch_json(URL))

    @app.page("/")
    def home(page):
        products.render(page)

        if products.loading:
            return art.Loader()
        if products.error:
            return art.Text(f"Couldn't load that: {products.error}")
        return art.Column([art.Text(p) for p in products.value])

`render(page)` is what makes this safe to call from a function that
re-runs constantly: it kicks off the fetch the *first* time it sees this
AsyncData, then does nothing on every subsequent re-render until you
explicitly call `.reset()` (handy for a pull-to-refresh button).
"""

from . import widgets


class AsyncData:
    def __init__(self, loader):
        self.loader = loader  # a zero-arg async function, e.g. lambda: art.fetch_json(url)
        self.value = None
        self.error = None
        self.loading = False
        self._started = False

    def render(self, page):
        """Call this at the top of your page function. Starts the fetch
        the first time; a no-op on every re-render after that."""
        if self._started:
            return
        self._started = True
        self.loading = True
        self.error = None

        async def run():
            try:
                self.value = await self.loader()
            except Exception as exc:
                self.error = str(exc)
            finally:
                self.loading = False
                if widgets._rerender:
                    widgets._rerender()

        page.run_task(run)

    def reset(self):
        """Forces the next render() call to fetch again - wire this up to
        a "refresh" button's on_click."""
        self._started = False
        self.value = None
        self.error = None
        self.loading = False
