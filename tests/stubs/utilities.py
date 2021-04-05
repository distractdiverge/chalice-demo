import os
import json


def read_json_file(path):
    filepath = f"{os.getcwd()}{path}"
    with open(filepath, "r") as f:
        contents = f.readlines()
        response = json.loads("\n".join(contents))

    return response
