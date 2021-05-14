# vaccine-notifi-bot
Code to send cowin vaccine slots availability notifications over telegram


## Getting the bot running:

1. Get a cloud VM. Oracle cloud gives two for free. Choose any India region while signing up. Other regions may get rate limited.
2. install python,pip and telegram-send
   - `sudo apt-get install python3 python3-pip`
   - `pip3 install telegram-send`
3. Run telegram-send to send messages in a group 
   - run `telegram-send --configure-group` and follow the instructions on screen. It will involve through creating a bot, group and adding the bot to group
   - test out teelgram send: run  `telegram-send "hello world"`
4. Configure your district:
   - to get state ID use:
       ```curl -X GET "https://cdn-api.co-vin.in/api/v2/admin/location/states" -H "accept: application/json" -H "Accept-Language: hi_IN"```
   - use the state id to get district info.:
       ```curl -X GET "https://cdn-api.co-vin.in/api/v2/admin/location/districts/16" -H "accept: application/json" -H "Accept-Language: hi_IN"``` 
   - edit the python file and put in your district ID
6. Run the runme.sh in screen. This will keep polling the api and send a message in the group is slots are open.
   - run `screen` and then  `runme.sh`
   - if you want to keep getting messages for empty slots run `screen` and then `runme.sh debug`

## How to book a slot

autobook.py provides the means to check and book the first slot that is available. 

Using it:
1. Get a login token from cowin.
 
   `login on cowin, open browser dev console -> applications -> session storage -> selfregistration.cowin.gov.in -> usertoken`
2. Put the token in the TOKEN constant. Note that token will only be valid for 15 minutes.
3. Enter the preferred city and pin code in the constants. From all the available slots for the district, the script will first try to book centers in this city and pin.
4. Enter the district and date. 
5. The code extracts the benificiary details from the token. If you want to book for someone else, change it in book_appointment()
6. Run `python3 autobook.py`
7. If slots are available, it will try to book it. Preferred timeslot will be the first one of the day 
8. The captcha will be opened in the default program for svg files 
9. Enter the captcha in the console
10. Appointment id will be logged in the console. Can also check in cowin.
