#!/bin/bash
bin_path="$HOME/.local/bin/bashelle"
source="https://github.com/Bashelle/cli/releases/download/v0.1.0/bashelle"
source_hash="63c61a1154f578e255e6b7c3f1469cfc20eb682d82980502fcabac9bab5c1de5"

case "$1" in
    "install")
        curl -Ls -o "$bin_path" "$source"

        if echo "$source_hash  $bin_path" | sha256sum -c - > /dev/null
        then
            chmod +x "$bin_path"
            exit 0
        else
            rm -f "$bin_path"
            exit 1
        fi
    ;;
    "remove")
        if [ -f "$bin_path" ]; then
            rm -f "$bin_path"
        fi
    ;;
esac

