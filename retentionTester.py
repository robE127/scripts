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

# Remove access to /etc/ntp.conf to prevent time from reverting
subprocess.call("chmod 000 /etc/ntp.conf", shell=True)

# Run 3 backups
for i in range(1,3):
    # Start a backup
	subprocess.call(START_BACKUP + agent, shell=True)
	# Get the current time in EPOCH format
	setTime = calendar.timegm(time.gmtime())
	# Go back in time by i hours
	setTime = setTime - (HOUR * i)
	subprocess.call("date -s @" + str(setTime), shell=True)
