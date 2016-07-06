!/bin/bash

globalKeys=(maxBackups backupOffset useAdvancedAlerting cefActive 
    disableScreenshots useRDPConnection autoDiffMerge defaultTP
    screenshot.queue)

agentKeys=(interval backupPause offsiteControl schedule retention
    offsiteRetention backupEngine screenshotVerification
    screenshotNotification emails include shareCompatibility
    vboxSettings esxSettings writeCache doDiffMerge vssExclude legacyVM
    snapTimeout)

homeKeys=(txSpeed speedLimit delay delayStart)

etcKeys=(exports hostname hosts ntp.conf resolv.conf)

inotifywait -m -q --format '%w %e %f' -e attrib,close_write,create,delete,delete_self \
    /datto/config /datto/config/keys /home/_config /etc/network/interfaces /etc |
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

        elif [ "$directory" = "/home/_config/"  ]; then
            for key in "${homeKeys[@]}"; do
                if [ "$filename" = "$key" ]; then
                    echo -n "$filename ($events): "
                    echo -e `cat "$directory$filename"`
                fi
            done

        elif [ "$directory" = "/datto/config/sync/" ] &&
                 [ "$filename" = "options" ]; then
                    echo -n "$filename ($events): "
                    echo -e `cat "$directory$filename"`

        elif [ "$directory" = "/etc/network/interfaces" ]; then
                    echo -n "$directory ($events): "
                    echo -e `cat "$directory"`

        elif [ "$directory" = "/etc/" ]; then
            for key in "${etcKeys[@]}"; do
                if [ "$filename" = "$key" ]; then
                    sleep 1
                    echo -n "$filename ($events): "
                    echo -e `cat "$directory$filename"`
                fi
            done
        fi
    done
