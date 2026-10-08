from datetime import datetime, timedelta, timezone
import http.client
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import time
import sys
import ssl
import requests
import config

authorization = 'Bearer ' + config.xurrent_token.strip()   # Xurrent personal access token
xurrent_url = "https://api.xurrent.com/v1/requests/open"   # Xurrent API (open requests only)

relay_gpio = 12
noalarmsleep = 60
alarmtriggersleep = 30
rechecksleep = 30

def makeanoise(pin, seconds):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        p = GPIO.PWM(pin, 2)  # channel=12 frequency=2Hz (TaskCall uses 5Hz, so Xurrent sounds slower)
        p.start(50)
        time.sleep(seconds)
        p.stop()
    finally:
        GPIO.cleanup()

def checkalarms():
    try:

        now_utc = datetime.now(timezone.utc)
        # Unassigned for longer than this many minutes (from config)
        cutoff = now_utc - timedelta(minutes=config.xurrent_unassigned_minutes)

        url = xurrent_url

        # Let Xurrent do the filtering: no Member, created before the cutoff
        params = {
            "fields": "id,subject,team,member,created_at",
            "per_page": 100,
            "member": "",
            "created_at": "<" + cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        count = 0
        while url:
            response = requests.get(
                url,
                params=params,
                headers={'Authorization': authorization, 'X-Xurrent-Account': config.xurrent_account},
                timeout=30
            )

            if response.status_code != 200:
                print("Got response {} from server".format(response.status_code))
                return -3

            data = response.json()

            # Count Command Centre requests that nobody has picked up
            for req in data:
                team = req.get('team') or {}
                if team.get('name') != config.xurrent_team:
                    continue
                if req.get('member'):
                    continue
                print("Unassigned request {} - {}".format(req['id'], req.get('subject', '')))
                count += 1

            # Xurrent returns 100 per page; follow the "next" link for more
            url = response.links.get('next', {}).get('url')
            params = None

        if count != 0:
            return 1
        return 0

    except requests.exceptions.ConnectionError:
        print("Error: {}".format(sys.exc_info()[0]))
        return -1
    except Exception:
        print("Error: {}".format(sys.exc_info()[0]))
        return -2

makeanoise(relay_gpio, 0.2)

while 1 < 2:
    alarmsactive = checkalarms()
    if alarmsactive == 1:
        makeanoise(relay_gpio, 0.2)
        print("active alarms, checking in {}s".format(alarmtriggersleep))
        time.sleep(alarmtriggersleep)
        alarmsactive = checkalarms()
        duration = 1
        while alarmsactive == 1:
            print("active alarms, making a noise!")
            makeanoise(relay_gpio, duration)
            print("rechecking in {}s".format(rechecksleep))
            time.sleep(rechecksleep)
            alarmsactive = checkalarms()
            duration = duration + 2
    elif alarmsactive == -1:
        print("Connection error")
        makeanoise(relay_gpio, 0.1)
        time.sleep(noalarmsleep)
    elif alarmsactive == -2:
        print("Other error")
        makeanoise(relay_gpio, 0.1)
        time.sleep(noalarmsleep)
    elif alarmsactive == -3:
        print("Response code error")
        makeanoise(relay_gpio, 0.1)
        time.sleep(noalarmsleep)
    else:
        print("No alarms, going to sleep for {}s".format(noalarmsleep))
        time.sleep(noalarmsleep)
