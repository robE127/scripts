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

# Prompt the user for the system to test with
agent = raw_input("What existing agent do you want to test with? ")

# Pause automatic backups for the agent
backupPause = open(CONFIG_KEYS + agent + PAUSE_KEY, 'w')
backupPause.write("1")
backupPause.close()

# Change the local retention settings to NEVER for ALL fields.
retentionSettingsFile = open(CONFIG_KEYS + agent + RETENTION_KEY, 'w')
retentionSettingsFile.write(SAFE_RETENTION)
retentionSettingsFile.close()

# Remove access to /etc/ntp.conf and /etc/cron.d/datto-codebase-core to prevent time from reverting
subprocess.call("chmod 000 /etc/ntp.conf", shell=True)
subprocess.call("chmod 000 /etc/cron.d/datto-codebase-core", shell=True)

realTime = calendar.timegm(time.gmtime())
fakeTime = realTime

# Run 3 backups a day for roughly 3 months
for d in range(1,92):
	for h in range(1,4):
		# Start a backup
		#print("Starting a backup at " + time.gmtime(fakeTime))
		subprocess.call(START_BACKUP + agent, shell=True)
		# Go back in time by h hours
		fakeTime = fakeTime - HOUR
		subprocess.call("date -s @" + str(fakeTime), shell=True)
	# Go back in time by (DAY * d) days from actual time each iteration
	subprocess.call("ntpdate ntp.dattobackup.com", shell=True)
	realTime = calendar.timegm(time.gmtime())
	fakeTime = realTime - (DAY * d)
	subprocess.call("date -s @" + str(fakeTime), shell=True)
	
# Return ntp config and time back to good state
subprocess.call("ntpdate ntp.dattobackup.com", shell=True)
subprocess.call("chmod 644 /etc/ntp.conf", shell=True)
subprocess.call("chmod 644 /etc/cron.d/datto-codebase-core", shell=True)