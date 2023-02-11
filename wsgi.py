import datetime
import os
from main import app
if __name__ == "__main__":
    app.run()
    if not os.path.exists("start.log"):
        with open("start.log", "w") as f:
            f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Started\n")

    with open("start.log", "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Started")