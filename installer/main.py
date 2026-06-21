from os import path, environ, mkdir, system
from collections import deque
from datetime import datetime

import traceback
import sys
from time import sleep
import json
import subprocess
import core
import ui
import os
import pacman

config = core.load_config(path.join(core.base_dir, "config.json"))

def greet():
    print(core.logo)
    print(f"Use {ui.IUP} {ui.IDOWN} to navigate")
    print(f"[Enter] to choose an option")
    print(f"[Ctrl+C] to close")

# Run some commands before installation
def before_install():
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP")

    if core.os_release() != "arch":
        raise Exception("this script only works on arch based distros :(")

    match current_desktop:
        case "Hyprland":
            subprocess.run(
                ["hyprctl", "eval", "hl.config({ misc = { disable_autoreload = true } })"],
                stdout=subprocess.DEVNULL
            )
    
def install():
    select_options = list(core.supported_desktops.keys()) + ["No thanks, i got my owns"]

    desktop = ui.select(title="Select target desktop dotfile:", options=select_options)
    desktop_alias = core.supported_desktops.get(desktop, "")
    dotfiles = config["dotfiles"]

    required_packages = config["packages"]["required"]
    
    if desktop_alias:
        required_packages += dotfiles[desktop]["dependencies"]
    else:
        ui.select(
            title="Tip: check documentation to know how to call some shortcuts in your desktop files!", 
            options=("Ok",)
        )

    dotfiles = config["dotfiles"]
    
    
    # Package installation
    pacman_packages, source_packages = ui.spinner(
        "Checking packages...", 
        pacman.check_packages, 
        required_packages,
        config["packages"]["source"]
    )

    if pacman_packages or source_packages:
        print("\nThe script will install the following packages")

        if pacman_packages:
            for pkg in pacman_packages: print("*", f"{ui.DIM} {pkg}{ui.RESET}")

        if source_packages:
            for pkg in source_packages: print("*", f"{ui.DIM} {pkg}{ui.RESET}")

        if ui.select("Do you agree?", ("Yes", "No")) == "Yes":
            if pacman_packages: pacman.install(pacman_packages)

            if source_packages:
                for pkg in source_packages:
                    script=path.join(core.script_dir, f"{pkg}.sh")

                    if path.isfile(script): 
                        subprocess.run([script, "install"])
                        print(f"{ui.GREEN}{ui.IOK}{ui.RESET} {pkg}")
                    else:                    
                        print(f"{ui.RED}{ui.IFAIL}{ui.RESET} '{pkg}.sh' script not found. Skipping...")
        else: sys.exit(0)
    
    # Backup
    backup_id=datetime.now().strftime("%Y%m%d%f")
    
    print("\nInstalling dotfiles...")
    
    # dotfile installation
    if desktop_alias and desktop in dotfiles:
        desktop_data = config["dotfiles"][desktop]
        core.backup(backup_id, path.join(core.config_home, desktop_alias))
        core.install_dotfile(desktop_data, desktop_alias)

    for dotfile, data in dotfiles.items():
        if dotfile != desktop and dotfile not in core.supported_desktops:
            core.backup(backup_id, path.join(core.config_home, dotfile))
            core.install_dotfile(data, dotfile)

def post_install():
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP")

    ui.spinner("Starting  'awww-daemon'...", core.start_daemons, ["awww-daemon"])
    
    if ui.select("Do you want to add custom wallpapers? (⚠️ some weeb wallpapers)", options=("Yes, please", "Nope")) == "Yes, please":
        wallpaper = path.join(core.config_home, "bashelle", "wallpapers", "wallpaper4.jpg")
        core.install_dotfile(config["optional"]["wallpapers"], "wallpapers", track=False)
        
        # sets the wallpapers
        subprocess.run(["awww", "img", wallpaper])
    
    subprocess.run(
        ["matugen", "color", "hex", "#ed8796"], 
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    )
    
    match current_desktop:
        case "Hyprland":
            subprocess.run(
                ["hyprctl", "eval", "hl.config({ misc = { disable_autoreload = false } })"],
                stdout=subprocess.DEVNULL
            )
            subprocess.run(["hyprctl", "reload"])
    
    ui.spinner("Starting  'quickshell'...", core.start_daemons, ["qs"])
    print(f"\n{ui.GREEN}{ui.IOK}{ui.RESET} installation completed!")
        
commands = deque([
    before_install, 
    greet,
    install,
    post_install
])

if config is not None:
    while commands:
        command = commands.popleft()       
        try: command()
        except Exception as e:
            print(f"\n{traceback.format_exc()}\n{e}")
            sys.exit(0)
else: 
    print(f"\n{ui.RED}Config file not found!{ui.RESET}")