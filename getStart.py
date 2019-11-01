import os

print "autostart added - Please note that your /etc/rc.local file is overwritten by this"
with open('/etc/rc.local','w') as fin:
	fin.write('#!/bin/sh -e\n')
        fin.write('#rc.local\n')
        fin.write('\n')
        fin.write('cd /home/pi/Desktop/sdk \n')
        fin.write('./start &\n')
        fin.write('exit 0\n')
