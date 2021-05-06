import logging
import sys
from datetime import datetime, timedelta
import requests
from requests import RequestException

URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}"
DISTRICTS = [151, 374]
# search for age limit less than:
AGE_LIMIT = 45
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
log = logging.getLogger()
log.addHandler(logging.FileHandler("debug.log"))
log.setLevel(logging.INFO)


def print_availability(data, debug_flag):
    for center in data['centers']:
        for session in center['sessions']:
            if session['min_age_limit'] < AGE_LIMIT:
                if debug_flag:
                    print(
                        f" {center['name']}, {center['district_name']} , {session['date']}, slots available: {session['available_capacity']}")
                if not debug_flag and session['available_capacity'] != 0:
                    print(
                        f" {center['name']}, {center['district_name']} , {session['date']}, slots available: {session['available_capacity']}")


def check_availability(districts, debug_flag):
    dates = []
    today = datetime.now().strftime("%d-%m-%Y")
    next_monday = (datetime.now() + timedelta(days=-datetime.now().weekday(), weeks=1)).strftime("%d-%m-%Y")
    dates.append(today)
    dates.append(next_monday)
    for district in districts:
        for date in dates:
            try:
                log.info("checking for district %s for date %s", district, date)
                response = requests.get(URL.format(district, date), headers={"user-agent": USER_AGENT})
                response.raise_for_status()
                print_availability(data=response.json(), debug_flag=debug_flag)
            except RequestException as ex:
                log.error("Error calling API. Mostly due to rate limiting")
                log.exception(ex)
                if response.status_code > 299:
                    print("Alert: IP blocked")
                if debug_flag:
                    print("Failed to fetch. Response was: %s", ex.response.text)


if __name__ == "__main__":
    debug = False
    if len(sys.argv) > 1:
        debug = sys.argv[1]
    check_availability(districts=DISTRICTS, debug_flag=debug)
