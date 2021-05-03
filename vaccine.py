import logging 
from datetime import date
import datetime
import json
import requests
import sys
from requests import RequestException

debug=False

log = logging.getLogger()
# make it print to the console.
console = logging.FileHandler("debug.log")
log.addHandler(console)
log.setLevel(logging.INFO)


if len(sys.argv) > 1:
  debug=sys.argv[1]

def print_available(res):
    for center in res['centers']:
      for session in center['sessions']:
        if session['min_age_limit'] < 45:
            if debug:
                print(f" {center['name']}, {center['district_name']} , {session['date']}, slots available: {session['available_capacity']}")
            if not debug and session['available_capacity'] != 0:
                print(f" {center['name']}, {center['district_name']} , {session['date']}, slots available: {session['available_capacity']}")
                #print(center['name'], center['district_name'], session['date'], session['available_capacity'])



district_ids =[151,152]
dates = []
today = date.today()
today = today.strftime("%d-%m-%Y")
dates.append(today)
today = datetime.date.today()
next_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
next_monday=next_monday.strftime("%d-%m-%Y")
dates.append(next_monday)
for district_id in district_ids:
    for date_check in dates:
        try:
            log.info(
                "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=%s&date=%s" % (
                district_id, date_check))
            res = requests.get(
                "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=%s&date=%s" % (
                district_id, date_check))
            res.raise_for_status()
            print_available(res.json())
        except RequestException as e:
            log.exception(e)
            if debug:
                print("exception while fetching message: %s", e.response.text)





