import eel

eel.init('web')

eel.start('loading.html', block=False, port=0)

eel.show("main.html")
eel.show("matches.html")
eel.show("options.html")
eel.show("standings.html")

while True:
    eel.sleep(1)
    print("Hello World")