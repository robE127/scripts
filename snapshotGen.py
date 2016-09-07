#!/usr/bin/python

import subprocess, time, calendar

print("***Please read carefully before using this script.***\n")

print("""This script will delete all snapshots for the existing agent
that you specify below. It will then replace them with the fake
snapshots created via this script. It will replace the recoveryPoints
key file with the new snapshots. It will remove the transfers
key file to avoid issues. It will mark all of the snapshots for speedsync.
Be aware, the date created zfs property will not be accurate for the
snapshots. This is not a problem because retention runs based on the
EPOCH time in the snapshot name.\n""")

print("Press CTRL+D or CTRL+C to exit\n")

agent = str(raw_input("What agent would you like to merge these fake snapshots with? "))

startDaysBack = int(raw_input("How many days back do you want to start your snapshots? "))

print("Now generating 3 snapshots every day from the specified amount of days...")

subprocess.call("snapctl renameAgent " + agent + " retentionTesting", shell=True)

subprocess.call("zfs destroy -r homePool/home/agents/retentionTesting", shell=True)

subprocess.call("zfs create homePool/home/agents/retentionTesting", shell=True)

now = calendar.timegm(time.gmtime())

start = now - (startDaysBack * 24 * 60 * 60)

current = start

dayStartTime = start

while current < now:
    i = 0
    while i < 3:
        subprocess.call("zfs snapshot homePool/home/agents/retentionTesting@" + str(current), shell=True)
        current += (60 * 60)
        i += 1
    dayStartTime += (24 * 60 * 60)
    current = dayStartTime

subprocess.call("zfs list -t snapshot -r -o name -H homePool/home/agents/retentionTesting | xargs zfs set sync:devsnap=true", shell=True)

subprocess.call("zfs list -t snapshot -r -o name -H  homePool/home/agents/retentionTesting | awk -F '@' '{print $2}' > /datto/config/keys/retentionTesting.recoveryPoints", shell=True)

subprocess.call("speedsync refresh homePool/home/agents/retentionTesting", shell=True)

print("\nThe following snapshots have been generated:\n")

subprocess.call("zfs list -t snapshot -r -o name homePool/home/agents/retentionTesting -H | awk -F '@' '{print $2}' | xargs -i date -d@{}", shell=True)

print("\nHave Fun!\n")
