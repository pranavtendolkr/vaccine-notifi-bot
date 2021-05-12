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


CHECK_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}"
SCHEDULE_URL = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
CAPTCHA_URL = "https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha"

DISTRICT = 151
# one day will get us the entire week
DATE = "17-05-2021"
# search for age limit less than:
AGE_LIMIT = 45

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
HEADERS = {
    "content-type": "application/json",
    "user-agent": USER_AGENT,
    "Authorization": "Bearer " + TOKEN
}

log = logging.getLogger()
log.setLevel(logging.INFO)

# process:
# 1. check slots
def check_availability(district, date):
    try:
        log.info("checking for district %s for date %s", district, date)
        response = requests.get(CHECK_URL.format(district, date), headers={"user-agent": USER_AGENT})
        response.raise_for_status()
        return response.json()
    except RequestException as ex:
        log.error("Error calling API. Mostly due to rate limiting")
        log.exception(ex)


# 2. parse slots to get info for booking API
def parse_avalability(availability: dict):
    for center in availability['centers']:
        for session in center['sessions']:
            if session['min_age_limit'] < AGE_LIMIT and session["available_capacity"] < 0:
                return session['session_id'], session['slots']
    return None, None


def get_benificiary_from_token(token):
    _, data, _ = token.split('.')
    missing_padding = len(data) % 4
    if missing_padding:
        data += '='*missing_padding
    decoded_data = base64.b64decode(data)
    json_data = json.loads(decoded_data)
    return json_data.get('beneficiary_reference_id')


# 3. call booking API
def book_appointment(session_id, slots, token, captcha):
    benificiary = get_benificiary_from_token(token)
    post_payload = {
        "dose": 1,
        "session_id": session_id,
        "slot": slots[0],
        "beneficiaries": [benificiary],
        "captcha": captcha
    }
    response = requests.post(url=SCHEDULE_URL, headers=HEADERS, json=post_payload)
    print(response.text)


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
    session_id, slots = parse_avalability(availability)
    print(session_id, slots)
    if session_id:
        captcha = solve_captcha()
        book_appointment(session_id, slots, TOKEN, captcha)



