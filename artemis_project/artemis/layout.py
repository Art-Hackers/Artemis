"""
One function: pick a different control tree depending on how wide the
window currently is. Since Artemis re-renders the current screen on
window resize (wired up in App._build), calling this from inside your
page function gets you a genuinely responsive layout - same codebase,
different arrangement on a phone vs a desktop window - without touching
page.on_resize yourself.
"""


def responsive(page, mobile=None, tablet=None, desktop=None, tablet_at=600, desktop_at=1000):
    """
        art.responsive(page,
            mobile=art.Column([...]),
            desktop=art.Row([...]),
        )

    Only `mobile` is required - `tablet`/`desktop` fall back to the next
    size down if you don't provide them, so a two-way mobile/desktop split
    is just two arguments, not three.
    """
    width = page.width or 0

    if width >= desktop_at and desktop is not None:
        return desktop
    if width >= tablet_at and tablet is not None:
        return tablet
    return mobile
