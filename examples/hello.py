import artemis as art

app = art.App("Hello", theme="midnightblue")

@app.page("/")
def home(page):
    return art.Column([
        art.Title("Hello, Artemis"),
        art.Button("Say hi", color="arctic", on_click=lambda e: art.toast("hi!")),
    ], center=True)

app.run()