# vaccine-notifi-bot
Code to send cowin vaccine slots availability notifications over telegram


Steps:

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
