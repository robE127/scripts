#!/usr/bin/python

import sys, subprocess, time, calendar, logging

logging.basicConfig(level=logging.INFO, format='\n%(levelname)s - %(message)s')

msg = (

    '\n      ***Please read carefully before using this script.***\n'
    'This script will delete all snapshots for the existing agent that you\n'
    'specify below. It will then replace them with the fake snapshots created\n'
    'via this script. It will replace the recoveryPoints key file with the new\n'
    'snapshots\' epoch time. It will remove the transfers key file to avoid\n'
    'potential issues. It will mark all of the snapshots with sync:devsnap=true\n'
    'for speedsync. Be aware, the creation date zfs property will not be\n'
    'accurate for the fake snapshots. This is not a problem because retention\n'
    'runs based on the epcoh time in the snapshot name.\n')

print(msg)

print("\nPress CTRL+C to exit at any time.\n")

try:

    agent = str(raw_input("\nWhat agent would you like to use with the fake snapshots? "))

    startDaysBack = int(raw_input("\nHow many days back do you want to start your snapshots? "))

    snapsPerDay = int(raw_input("\nHow many snapshots do you want to create per day? "))

    logging.info('Removing any existing homePool/retentionTesting dataset...')
    subprocess.call("zfs destroy -r homePool/retentionTesting", shell=True)

    logging.info('Creating ZFS dataset...')
    subprocess.call("zfs create homePool/retentionTesting", shell=True)

    now = calendar.timegm(time.gmtime())

    start = now - (startDaysBack * 24 * 60 * 60)

    current = start

    dayStartTime = start

    logging.info('Creating snapshots...')
    while current < now:
        i = 0
        while i < snapsPerDay:
            subprocess.call("zfs snapshot homePool/retentionTesting@" + str(current), shell=True)
            lastSnap = str(current)
            current += (60 * 60)
            i += 1
        dayStartTime += (24 * 60 * 60)
        current = dayStartTime


    logging.info('Setting all sync:devsnap=true...')
    subprocess.call("zfs list -t snapshot -r -o name -H homePool/retentionTesting | xargs zfs set sync:devsnap=true", shell=True)

    logging.info('Destroying zfs dataset for specified agent...')
    subprocess.call('zfs destroy -r homePool/home/agents/' + agent, shell=True)

    logging.info('Zfs sending retentionTesting dataset...')
    subprocess.call('zfs send -R homePool/retentionTesting@' + lastSnap + ' | pv | zfs recv homePool/home/agents/' + agent, shell=True)

    logging.info('Generating new recoveryPoints key file...')
    subprocess.call("zfs list -t snapshot -r -o name -H  homePool/home/agents/" + agent + " | awk -F '@' '{print $2}' > /datto/config/keys/" + agent + ".recoveryPoints", shell=True)

    logging.info('Snapshots for the following times have been created for homePool/home/agents/' + agent + ':\n')
    subprocess.call("zfs list -t snapshot -r -o name -H homePool/home/agents/" + agent + " | awk -F '@' '{print $2}' | xargs -i date -d@{}", shell=True)

    print("\nHave Fun!\n")

except KeyboardInterrupt:
    print("\n")
    sys.exit()
