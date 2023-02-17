import os
import json

def list_flags():
    with open("list_flags.json", "w") as f:
        flags = []
        for file in os.listdir("flags"):
            print(file)
            if file.endswith(".svg"):
                if len(file) == 6 or len(file) == 7:
                    flags.append(file[:-4])
        print(flags)
        print(len(flags))
        f.write(json.dumps(flags))
        print("Done!")

    if "list_flags.json" in os.listdir():
        print("File created!")

if __name__ == "__main__":
    list_flags()