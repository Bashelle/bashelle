from datetime import datetime
from os import path
from urllib.parse import urlparse
from pathlib import Path

import shutil
import subprocess
import core
import ui
import os
import tarfile
import pacman
import json

def greet():
    print(core.logo)
    print(f"Use {ui.IUP} {ui.IDOWN} to navigate")
    print("[Enter] to choose an option")
    print("[Ctrl+C] to close")

# Loads config.json file
def load_config(file):
    if not path.isfile(file): 
        return None
    
    with open(file, "r") as f:
        return json.load(f)


# Run some commands before installation
def before_install():
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP")

    if core.os_release() != "arch":
        print("this script only works on arch based distros :(")
        exit(1)

    scripts_path = Path(core.script_dir)

    print("\nBefore anything happens, there is some scripts which may require permissions. (see scripts folder)")
    if ui.select("Grant permissions?", options=["Yes", "No"]) == 0:
        for path in scripts_path.iterdir():
            subprocess.run(["chmod", "+x", path])
    else: exit(0)

    match current_desktop:
        case "Hyprland":
            subprocess.run(
                ["hyprctl", "eval", "hl.config({ misc = { disable_autoreload = true } })"],
                stdout=subprocess.DEVNULL
            )

def select_desktop():
    desktop_options = list(core.supported_desktops.keys()) + ["No thanks, i got my owns"]
    select_option = ui.select(title="Select target desktop dotfile:", options=desktop_options)
    return core.supported_desktops.get(desktop_options[select_option], None)

def install_dependencies(required_packages, source_packages):
    required_packages, source_packages = ui.spinner(
        "Checking packages...", 
        pacman.check_packages, 
        required_packages, 
        source_packages
    )

    if required_packages or source_packages:
        print("This script will install the following packages:")
        
        for pkg in required_packages + source_packages: print(" L", pkg)
        
        if ui.select("Do you agree?", options=("yes", "no")) == 0:
            if required_packages: pacman.install(required_packages)
        
            if source_packages:
                for pkg in source_packages:
                    ui.spinner(f"Installing '{pkg}' from script", pacman.install_from_source, f"{pkg}.sh")

def backup(name):
    source     = path.join(core.config_home, "bashelle")
    backup_dir = path.join(core.config_home, "bashelle", ".recovery", f"{name}")

    shutil.copytree(
        source, 
        backup_dir,
        ignore=shutil.ignore_patterns(".recovery", "wallpapers")
    )

def install_dotfile(source, install_path):
    install_path = path.expanduser(install_path)
    
    os.makedirs(install_path, exist_ok=True)
    os.makedirs("/tmp/bashelle", exist_ok=True)
    
    filename = path.basename(urlparse(source).path)
    tmp = path.join("/tmp", "bashelle", filename)
    
    subprocess.run(["curl", "-sL", "-o", tmp, source], check=True)

    with tarfile.open(tmp, "r:*") as tar:
        members = []
        
        for member in tar.getmembers():
            path_frag = member.name.split("/")
            
            if len(path_frag) > 1:
                member.name = os.path.join(*path_frag[1:])
                members.append(member)
        
        tar.extractall(path=install_path, members=members)

def post_install():
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")

    match current_desktop:
        case "Hyprland":
            subprocess.run(
                ["hyprctl", "eval",
                    "hl.config({ misc = { disable_autoreload = false } })"],
                stdout=subprocess.DEVNULL
            )
            subprocess.run(["hyprctl", "reload"], stdout=subprocess.DEVNULL)

config = core.load_config(path.join(core.base_dir, "config.json"))

if config:
    required_packages = config["packages"]["required"]
    source_packages   = config["packages"]["source"]
    
    greet()
    before_install()
    target_desktop = select_desktop()
    
    if target_desktop:
        required_packages += config["dotfiles"][target_desktop]["dependencies"]
    else:
        ui.select(title="Tip: See docs to know how to call shortcuts", options=("Ok",))

    install_dependencies(
        required_packages=required_packages, 
        source_packages=source_packages
    )

    # Creates a backup
    backup_name = datetime.now().strftime("installer_%Y%m%d_%H%M%S_%f")
    backup(backup_name)

    dotfiles = {
        dotfile: data for dotfile, data in config["dotfiles"].items()
        if dotfile not in core.supported_desktops.values() or dotfile == target_desktop
    }

    lock_data = {
        "versions": {}
    }

    for dotfile, data in dotfiles.items():
        if dotfile not in core.supported_desktops.values():
            lock_data["versions"][dotfile] = {
                "hash":         data["hash"],
                "source":       data["source"],
                "install_path": data["install_path"],
                "version":      data["version"],
            }
        
        ui.spinner(
            f"Installing '{dotfile}'...",
            install_dotfile,
            source=data["source"],
            install_path=data["install_path"]
        )
    
    # Write the lock-json
    lock_path = path.join(core.config_home, "bashelle", ".versions-lock.json")

    with open(lock_path, "w") as lock:
        json.dump(lock_data, lock, indent=2)

    # Starts the awww-daemon
    subprocess.run(["awww-daemon"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # Generate matugen colors
    subprocess.run(["matugen", "color", "#ed8796"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    if ui.select("Do you want to add custom wallpapers? (⚠️ some weeb wallpapers)", options=("Yes, please", "Nope")) == 0:
        wallpaper = path.join(core.config_home, "bashelle","wallpapers", "wallpaper4.jpg")
        
        ui.spinner(
            "Installing wallpapers...", 
            install_dotfile,
            source=config["optional"]["wallpapers"]["source"],
            install_path=config["optional"]["wallpapers"]["install_path"]
        )

        # sets the wallpapers
        subprocess.run(["awww", "img", wallpaper])

    post_install()
    print("\nBashelle has been installed succesfully!")