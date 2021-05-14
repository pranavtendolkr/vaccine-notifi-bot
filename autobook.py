import base64
import json
import logging
import sys
from datetime import datetime, timedelta
import requests
from requests import RequestException
import subprocess, os, platform

# how to get token:
# login on cowin, open dev console -> applications -> session storage -> selfregistration.cowin.gov.in -> usertoken
# fill this in
TOKEN = ""
PREFERRED_PIN_CODE = "403507"
PREFERRED_CITY = "Mapusa"

# CHECK_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}"
CHECK_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={0}&date={1}"
SCHEDULE_URL = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
CAPTCHA_URL = "https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha"

DISTRICT = 151
# one day will get us the entire week
DATE = "15-05-2021"
# search for age limit less than:
AGE_LIMIT = 45

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
HEADERS = {
    "content-type": "application/json",
    "user-agent": USER_AGENT,
    "Authorization": "Bearer " + TOKEN
}

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
log.addHandler(handler)


# process:
# 1. check slots
def check_availability(district, date):
    try:
        log.info("checking for district %s for date %s", district, date)
        response = requests.get(CHECK_URL.format(district, date), headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except RequestException as ex:
        log.error("Error calling API. Mostly due to rate limiting")
        log.exception(ex)


# 2. parse slots to get info for booking API
def parse_avalability(availability: dict):
    available_slots = []
    for center in availability['centers']:
        for session in center['sessions']:
            if session['min_age_limit'] < AGE_LIMIT and session["available_capacity"] > 0:
                available_slot = {"session_id": session['session_id'],
                                  "slots": session['slots'],
                                  "name": center['name'],
                                  "pincode": center['pincode'],
                                  "date": session['date']
                                  }
                available_slots.append(available_slot)

    for count, available_slot in enumerate(available_slots):
        if PREFERRED_CITY.lower() in available_slot.get('name').lower():
            available_slots.insert(0, available_slots.pop(count))
        elif available_slot.get('pincode') == PREFERRED_PIN_CODE:
            available_slots.insert(0, available_slots.pop(count))
    return available_slots


def get_benificiary_from_token(token):
    _, data, _ = token.split('.')
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    decoded_data = base64.b64decode(data)
    json_data = json.loads(decoded_data)
    return json_data.get('beneficiary_reference_id')


# 3. call booking API
def book_appointment(available_slots, token):
    benificiary = get_benificiary_from_token(token)
    for available_slot in available_slots:
        log.info("trying to book %s", str(available_slot))
        captcha = solve_captcha()
        post_payload = {
            "dose": 1,
            "session_id": available_slot.get('session_id'),
            "slot": available_slot.get('slots')[0],
            "beneficiaries": [benificiary],
            "captcha": captcha
        }
        response = requests.post(url=SCHEDULE_URL, headers=HEADERS, json=post_payload)
        print(response.text)
        if response.status_code == 200:
            break


def solve_captcha():
    response = requests.post(CAPTCHA_URL, headers=HEADERS)
    svg = response.json()['captcha']
    svg.replace("\\", "")
    with open("captcha.svg", "w") as f:
        f.write(svg)
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', f.name))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(f.name)
    else:  # linux variants
        subprocess.call(('xdg-open', f.name))
    captcha_text = input("enter captcha")
    return captcha_text


if __name__ == "__main__":
    if len(sys.argv) > 1:
        TOKEN = sys.argv[1]
    availability = check_availability(district=DISTRICT, date=DATE)
    available_slots = parse_avalability(availability)
    log.info(available_slots)
    if available_slots:
        book_appointment(available_slots, TOKEN)
