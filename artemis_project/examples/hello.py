import artemis as art

app = art.App("Hello", theme="ocean")

@app.page("/")
def home(page):
    return art.Column([
        art.Title("Hello, Artemis"),
        art.Button("Say hi", on_click=lambda e: print("hi!")),
    ], center=True)

app.run()