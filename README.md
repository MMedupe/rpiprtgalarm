# rpiprtgalarm

The purpose of this utility is to activate a buzzer on configurable intervals with configurable pulses if any unacknowledged alarms exist in PRTG or OpsGenie for longer than a conifgurable duration. 

Default configuration is to check every 60s for unacknowledged alerts.
If none found, it sleeps for 60s and rechecks.
If found, it sleeps for 30s and checks again
If still unacknowledged, the active alarming logic is executed.

This logic pulses the buzzer on and off for 1 second with 0.1s durations, sleeps 30s, checks for unacklowledged alarms, and if still present, repeats the cycle until alarms are acknowledged in PRTG or OpsGenie. Every 30 seconds the buzzer duration is increased by 2 seconds, i.e. 1s, 3s, 5s, 7s, 9s, etc.

## OpsGenie Installation
* clone the repo
* Copy rpiopsgeniealarm.service from _local cloned folder_/lib/systemd/system to /etc/systemd/system
* Create config.py in /home/pi with _geniekey="your OpsGenie key"_ as only content
* Run _systemctl start rpiopsgeniealarm.service_
* Run _systemctl enable rpiopsgeniealarm.service_
  
## Xurrent Installation
getxurrentunassigned.py sounds the buzzer when an open Xurrent request for a team (default Command Centre) has had no Member assigned for longer than a configurable number of minutes. It uses the same check/sleep/pulse logic as gettaskcall.py, but pulses at 2Hz instead of 5Hz so it sounds different from the TaskCall alarm.
* clone the repo
* Copy getxurrentunassigned.py to /home/pi
* Copy rpixurrentalarm.service from _local cloned folder_/lib/systemd/system to /etc/systemd/system
* Add the following to config.py in /home/pi (never commit config.py, it is in .gitignore):
  * _xurrent_token = 'your Xurrent personal access token'_ (scope: Allow, Request, Read)
  * _xurrent_account = 'ecentric-support'_
  * _xurrent_team = 'Command Centre'_
  * _xurrent_unassigned_minutes = 5_
* Run _systemctl start rpixurrentalarm.service_
* Run _systemctl enable rpixurrentalarm.service_

To debug, stop the service using _systemctl stop rpixurrentalarm.service_ and run _python3 getxurrentunassigned.py_ in a terminal and observe the output.

## Debugging
Stop the service using _systemctl stop rpiopsgeniealarm.service_ and run _python3 getopsgenie.py_ in a terminal and observe the output
  
## checkwifi
There is a checkwifi.sh script in lib/usr/local/bin that pings an address and reboots the pi if no response received. This became necessary because the wifi connection on my pi zero would disconnect and not reconnect, therefor one would have no way to reach the raspberry pi.
There is a sample crontab in lib/var/spool/cron/crontabs to schedule checkwifi.sh
There is a sample logrorate config in lib/etc/logrorate.d/checkwifi to rotate /var/log/checkwifi
  
## Prerequisites
Raspberry Pi OS Lite bullseye required no other packages to be installed
