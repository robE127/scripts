#


#!/usr/bin/python

import subprocess, calendar, time

# Constants for different amount of time periods in seconds
HOUR = 3600
DAY = 86400
WEEK = 604800
MONTH = 2629743
YEAR = 31556926

# Other constants
CONFIG_KEYS = "/datto/config/keys/"
RETENTION_KEY = ".retention"
PAUSE_KEY = ".backupPause"
ZFS_AGENT_PATH = "homePool/home/agents/"
SAFE_RETENTION = "240000:240000:240000:240000"
START_BACKUP = "snapctl foregroundStart "
OFFSITE_CONTROL_KEY = ".offsiteControl"

# Prompt the user for the system to test with
agent = raw_input("What existing agent do you want to test with:  ")
testLength = raw_input("How many months of backups do you want to create: ")

# Pause automatic backups for the agent
backupPause = open(CONFIG_KEYS + agent + PAUSE_KEY, 'w')
backupPause.write("1")
backupPause.close()

# Set offsite to never because I think going back in time is going to confuse speedsync.
offsiteControl = open(CONFIG_KEYS + agent + OFFSITE_CONTROL_KEY, 'w')
offsiteControl.write('{"interval":"-1","latestSnapshot":"0","latestOffsiteSnapshot":"0"}')
offsiteControl.close()

# Change the local retention settings to NEVER for ALL fields.
retentionSettingsFile = open(CONFIG_KEYS + agent + RETENTION_KEY, 'w')
retentionSettingsFile.write(SAFE_RETENTION)
retentionSettingsFile.close()

# Remove access to /etc/ntp.conf and /etc/cron.d/datto-codebase-core to prevent time from reverting
subprocess.call("chmod 000 /etc/ntp.conf", shell=True)
subprocess.call("chmod 000 /etc/cron.d/datto-codebase-core", shell=True)

# Get the current time, convert to EPOCH format, and start at fakeTime.
realTime = calendar.timegm(time.gmtime())
fakeTime = realTime - (MONTH * int(testLength))
startFakeTime = fakeTime
subprocess.call("date -s @" + str(fakeTime), shell=True)

# Run 3 backups a day for roughly 3 months
for d in range(1,92):
	for h in range(1,4):
		# Start a backup
		# print("Starting a backup at " + str(time.gmtime(fakeTime))) # This is just for debugging.
		subprocess.call(START_BACKUP + agent, shell=True)
		# Go forward in time by h hours
		fakeTime = fakeTime + HOUR
		subprocess.call("date -s @" + str(fakeTime), shell=True)
		time.sleep(3)
	# Go forward in time by (DAY * d) days from startFakeTime
	fakeTime = startFakeTime + (DAY * d)
	subprocess.call("date -s @" + str(fakeTime), shell=True)
	time.sleep(3)
	
# Return ntp config and time back to normal state
subprocess.call("ntpdate ntp.dattobackup.com", shell=True)
subprocess.call("chmod 644 /etc/ntp.conf", shell=True)
subprocess.call("chmod 644 /etc/cron.d/datto-codebase-core", shell=True)