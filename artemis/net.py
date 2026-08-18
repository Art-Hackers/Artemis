"""
Network calls, for the "load some data when the screen opens" case every
real app eventually needs. Built on httpx, which is already a dependency
of Flet itself (Artemis doesn't add anything new here) - these are just
thin async wrappers with sane defaults (a timeout, `raise_for_status`)
so you're not repeating the same six lines of client/response/error
handling boilerplate in every screen that talks to an API.

    async def load(e):
        items.value = await art.fetch_json("https://api.example.com/items")
        # _after()'s auto-redraw (see widgets.py) repaints once this returns

    art.Button("Refresh", on_click=load)

Every function here is a plain `async def` - use them from an async
on_click/on_change (or anywhere else already inside an event loop), the
same as any other await.
"""

import httpx

DEFAULT_TIMEOUT = 10


async def fetch_json(url, timeout=DEFAULT_TIMEOUT, **kwargs):
    """GETs a URL and returns the parsed JSON body. Raises
    httpx.HTTPStatusError on a non-2xx response - wrap in a try/except if
    you want to handle failures inline rather than letting the error
    boundary catch it."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, **kwargs)
        response.raise_for_status()
        return response.json()


async def fetch_text(url, timeout=DEFAULT_TIMEOUT, **kwargs):
    """Same as fetch_json but returns the raw response body as text -
    for APIs that don't return JSON, or when you want to parse it
    yourself."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, **kwargs)
        response.raise_for_status()
        return response.text


async def post_json(url, data=None, timeout=DEFAULT_TIMEOUT, **kwargs):
    """POSTs a dict as a JSON body and returns the parsed JSON response."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=data, **kwargs)
        response.raise_for_status()
        return response.json()
