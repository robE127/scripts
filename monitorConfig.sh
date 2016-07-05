#!/bin/bash

globalKeys=(maxBackups backupOffset useAdvancedAlerting cefActive 
    disableScreenshots useRDPConnection autoDiffMerge defaultTP
    screenshot.queue)
agentKeys=(interval backupPause offsiteControl schedule retention
    offsiteRetention backupEngine screenshotVerification
    screenshotNotification emails include shareCompatibility
    vboxSettings esxSettings writeCache doDiffMerge)

inotifywait -r -m -q -e close_write,create,delete /datto/config |
    while read -r directory events filename; do
        if [ "$directory" = "/datto/config/" ]; then
            for key in "${globalKeys[@]}"; do
                if [ "$filename" = "$key" ]; then
                    echo -n "$filename ($events): "
                    echo -e `cat "$directory$filename"`
                fi
            done
        elif [ "$directory" = "/datto/config/keys/" ]; then
             for key in "${agentKeys[@]}"; do
                if [ "${filename##*.}" = "$key" ]; then
                    echo -n "$filename ($events): "
                    echo -e `cat "$directory$filename"`
                fi
            done
        fi
    done
