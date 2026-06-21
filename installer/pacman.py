import ui
import subprocess
import core
import shutil

from os import path

# install a list of packages
def install(pkgs) -> None:
    subprocess.run(["sudo", "-v"])

    for pkg in pkgs:
        cmd = ["sudo", "pacman", "-S", "--noconfirm", "--needed", pkg]
        ui.spinner(
            f"{pkg}", 
            subprocess.run, cmd,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            check=True
        )

# check if a package exists
def package_exists(pkg) -> bool:
    cmd = ["pacman", "-Qq", pkg]
    process = subprocess.run(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    return process.returncode == 0

# get the missing dependences
def check_packages(pacman, source):
    bin_path=path.join(core.local_home, "bin")
    missing_source=[]
    missing_pacman=[]
    
    for pkg in pacman:
        exists = package_exists(pkg)
        if not exists: missing_pacman.append(pkg)

    for pkg in source:
        exists = path.exists(f"{bin_path}/{pkg}") or shutil.which(pkg) is not None
        
        if not exists:
            missing_source.append(pkg)

    return missing_pacman, missing_source

# remove a list of packages
def remove(pkgs) -> None:
    subprocess.run(["sudo", "-v"])
    for pkg in pkgs:
        cmd = ["sudo","pacman", "-Rns", "--noconfirm", pkg]            
        ui.spinner(
            f"{pkg}", 
            subprocess.run, cmd,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            check=True
        )