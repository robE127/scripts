#!/usr/bin/python

import sys, subprocess, time, calendar, logging

logging.basicConfig(level=logging.INFO, format='\033[0;36m' + '\n%(levelname)s - %(message)s' + '\033[0m')

msg = (

    '\33[0;31m'
    '\n      ***Please read carefully before using this script.***\n'
    'This script will delete all snapshots for the existing agent that you\n'
    'specify below. It will then replace them with the snapshots created\n'
    'via this script. Be aware, the creation date zfs property will not be\n'
    'accurate for these snapshots. This is not a problem because retention\n'
    'runs based on the epoch time in the snapshot name.\n'
    '\33[0m'
)

print(msg)

print("\nPress CTRL+C to exit at any time.\n")

try:

    agent = str(raw_input("\nWhat existing agent would you like to create snapshots for? "))

    startDaysBack = int(raw_input("\nHow many days back do you want to start your snapshots? "))

    snapsPerDay = int(raw_input("\nHow many snapshots do you want to create per day? "))

    logging.info('Touching inhibitAllCron')
    subprocess.call("touch /datto/config/inhibitAllCron", shell=True)

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

    # Uncomment if you want to sync these snapshots offsite
    #logging.info('Setting all sync:devsnap=true...')
    #subprocess.call("zfs list -t snapshot -r -o name -H homePool/retentionTesting | xargs zfs set sync:devsnap=true", shell=True)

    logging.info('Destroying zfs dataset for specified agent...')
    subprocess.call("zfs destroy -r homePool/home/agents/" + agent, shell=True)

    logging.info('Zfs sending retentionTesting dataset...')
    subprocess.call("zfs send -R homePool/retentionTesting@" + lastSnap + " |  zfs recv homePool/home/agents/" + agent, shell=True)

    logging.info('Generating new recoveryPoints key file...')
    subprocess.call("zfs list -t snapshot -r -o name -H  homePool/home/agents/" + agent + " | awk -F '@' '{print $2}' > /datto/config/keys/" + agent + ".recoveryPoints", shell=True)

    logging.info('Blanking out the transfers key file...')
    subprocess.call("echo '' > /datto/config/keys/" + agent + ".transfers", shell=True)

    logging.info('Removing inhibitAllCron...')
    subprocess.call("rm /datto/config/inhibitAllCron", shell=True)

    logging.info(str(snapsPerDay * startDaysBack) + ' snapshots with the following timestamps have been created for homePool/home/agents/' + agent + ':\n')
    subprocess.call("zfs list -t snapshot -r -o name -H homePool/home/agents/" + agent + " | awk -F '@' '{print $2}' | xargs -i date -d@{}", shell=True)

    print("\nHave Fun!\n")

except KeyboardInterrupt:
    print("\n")
    sys.exit()
