#!/bin/bash

keys=(maxBackups backupOffset useAdvancedAlerting cefActive disableScreenshots useRDPConnection autoDiffMerge defaultTP)

inotifywait -m -q -e close_write,create,delete /datto/config |
    while read -r directory events filename; do
        for key in "${keys[@]}"; do
            if [ "$filename" = "$key" ]; then
                echo -n "$filename ($events): "
                echo -e `cat "$directory$filename"`
            fi
        done
    done
