#!/bin/bash
dependencies=("rust")
clean_pkgs=()

local="$HOME/.local"

resolve_dependencies() {
    for dep in "${dependencies[@]}"; do
        if ! pacman -Qq "$dep" &> /dev/null; then
            clean_pkgs+=("$dep")
        fi
    done

    if [[ ${#clean_pkgs[@]} -gt 0 ]]; then
        sudo pacman -S --noconfirm "${clean_pkgs[@]}"
    fi
}

clean() {
    if [[ ${#clean_pkgs[@]} -gt 0 ]]; then
        echo -e "\rCleaning...\n"
        sudo pacman -Rns --noconfirm "${clean_pkgs[@]}" &> /dev/null
    fi
}


case "$1" in
    "install")
        if [ ! -f "$local/bin/wl-gammarelay-rs" ]; then   
            resolve_dependencies
            echo -e "wl-gammarelay-rs take some time, please wait 😔👊\n"
            echo -e "Compiling...\n"
            cargo install wl-gammarelay-rs --root "$local"
            clean
        fi
    ;;
    "remove")
        if [ -f "$local/bin/wl-gammarelay-rs" ]; then
            rm -f "$local/bin/wl-gammarelay-rs"
        fi
    ;;
esac