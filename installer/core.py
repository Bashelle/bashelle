from platform import freedesktop_os_release
from os import path

import json
import shutil

logo       = r'''
    ▄▄▄                          ▄▄ ▄▄       
   ██▀▀█▄             █▄          ██ ██      
   ██ ▄█▀             ██          ██ ██      
   ██▀▀█▄ ▄▀▀█▄ ▄██▀█ ████▄ ▄█▀█▄ ██ ██ ▄█▀█▄
 ▄ ██  ▄█ ▄█▀██ ▀███▄ ██ ██ ██▄█▀ ██ ██ ██▄█▀
 ▀██████▀▄▀█▄███▄▄██▀▄██ ██▄▀█▄▄▄▄██▄██▄▀█▄▄▄                                        
                 by anzar
'''

base_dir    = path.join(path.dirname(__file__))
script_dir  = path.join(base_dir, "scripts")

config_home   = path.expanduser("~/.config")
local_home    = path.expanduser("~/.local")

supported_desktops = {
    "hyprland": "hypr"
}

def os_release() -> str:
    release = freedesktop_os_release()
    id      = release.get("ID", "")
    id_like = release.get("ID_LIKE", "")
    
    if (id == "arch" or "arch" in id_like):
        return "arch"
        
    return "not_supported"

def load_config(file):
    if not path.isfile(file): 
        return None
    
    with open(file, "r") as f:
        return json.load(f)

def backup(name):
    source = path.join(config_home, "bashelle")
    backup_dir = path.join(config_home, "bashelle", ".recovery", f"{name}")

    shutil.copytree(
        source, 
        backup_dir,
        ignore=shutil.ignore_patterns(".recovery")
    )