import os
import json
import platform

options = {"Current-theme": 
{"Code":{
    "fast-movers": "#00ffff",
    "slow-movers": "#1e90ff",
    "stoppers": "#7fffd4",
    "setters": "#ff8c00",
    "returners": "#ff6347",
    "inputs": "#00ff00",
    "calculators": "#ffc0cb",
    "numbers": "#ffff00",
    "comment": "#808080",
    "nest-mod1": "#ee82ee",
    "nest-mod2": "#4169e1",
    "nest-mod0": "#ffd700",
    "keyword": "#ff00ff",
    "variable": "#7cfc00",
    "string": "#ff3030",
    "backslash": "#fa8072",
    "comment-backslash": "#424242",
    "custom-function-parameter": "#e066ff",
    "custom-function": "#c6e2ff",
    "error": "#ff0000"},
"Output":{
    "z-label": "#00ffff",
    "x-label": "#ee82ee",
    "label": "#ff8c00",
    "warning": "#ff6347",
    "text": "#ffd700",
    "positive-number": "#00ff00",
    "negative-number": "#ff6347",
    "placeholder": "#808080"
}
},
"Themes": {
    "Default": {"Code":{
        "fast-movers": "cyan",
        "slow-movers": "dodger blue",
        "stoppers": "aquamarine",
        "setters": "dark orange",
        "returners": "tomato",
        "inputs": "lime",
        "calculators": "pink",
        "numbers": "yellow",
        "comment": "gray",
        "nest-mod1": "violet",
        "nest-mod2": "royal blue",
        "nest-mod0": "gold",
        "keyword": "magenta",
        "variable": "lawn green",
        "string": "firebrick1",
        "backslash": "salmon",
        "comment-backslash": "gray26",
        "custom-function-parameter": "MediumOrchid1",
        "custom-function": "SlateGray1",
        "error": "red"},
    "Output":{
        "z-label": "cyan",
        "x-label": "violet",
        "label": "dark orange",
        "warning": "tomato",
        "text": "gold",
        "positive-number": "lime",
        "negative-number": "tomato",
        "placeholder": "gray"
    }
    }
}, 
"Settings": {"Ask before deleting a cell": False},
"Show-tutorial": True
}

def get_path_to_options():
    operating_system = platform.system()
    if operating_system == "Windows":
        return os.path.join(os.path.expanduser("~"), "AppData\\Roaming\\Mothball\\Mothball Settings\\Options.json")
    elif operating_system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library\\Application Support\\Mothball\\Mothball Settings\\Options.json")

def create_directories():
    operating_system = platform.system()
    if operating_system == "Windows":
        create_windows_directories()
    elif operating_system == "Darwin":
        create_mac_directories()

def create_windows_directories():
    user_directory = os.path.expanduser("~")
    os.makedirs(os.path.join(user_directory, "AppData\\Roaming\\Mothball\\Mothball Settings"), exist_ok=True)
    os.makedirs(os.path.join(user_directory, "Documents\\Mothball\\Notebooks"), exist_ok=True)

    if not os.path.exists(os.path.join(user_directory, "AppData\\Roaming\\Mothball\\Mothball Settings\\Options.json")):
        with open(os.path.join(user_directory, "AppData\\Roaming\\Mothball\\Mothball Settings\\Options.json", "w")) as file:
            json.dump(options, file)   

def create_mac_directories():
    user_directory = os.path.expanduser("~")
    os.makedirs(os.path.join(user_directory, "Library\\Application Support\\Mothball\\Mothball Settings"), exist_ok=True)
    os.makedirs(os.path.join(user_directory, "Documents\\Mothball\\Notebooks"), exist_ok=True)

    if not os.path.exists(os.path.join(user_directory, "Library\\Application Support\\Mothball\\Mothball Settings\\Options.json")):
        with open(os.path.join(user_directory, "Library\\Application Support\\Mothball\\Mothball Settings\\Options.json", "w")) as file:
            json.dump(options, file)


def get_options():
    operating_system = platform.system()
    if operating_system == "Windows":
        return get_windows_options()
    elif operating_system == "Darwin":
        return get_mac_options()

def get_windows_options():
    with open(os.path.join(os.path.expanduser("~"), "AppData\\Roaming\\Mothball\\Mothball Settings\\Options.json")) as file:
        return json.load(file)

def get_mac_options():
    with open(os.path.join(os.path.expanduser("~"), "Library\\Application Support\\Mothball\\Mothball Settings\\Options.json")) as file:
        return json.load(file)