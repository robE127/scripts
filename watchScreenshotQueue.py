#!/usr/bin/python

# This script will seek and print the current size of the screenshot queue with a timestamp.

import time

screenshotFile = open("/datto/config/screenshot.queue")
screenshotFile.seek(2)
number = screenshotFile.read(2)
screenshotFile.close()
print (time.strftime("%H:%M:%S: ")) + number