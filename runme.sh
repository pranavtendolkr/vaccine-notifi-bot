#!/bin/bash

# $1 == debug

while true
do
        OUTPUT=$(python3 vaccine.py $1)
        telegram-send --config ~/.config/telegram-send.conf "$OUTPUT"
	echo "Press [CTRL+C] to stop.."
	sleep 15m
done




#OUTPUT=$(python3 vaccine.py debug)
#telegram-send --config /home/ubuntu/.config/telegram-send.conf "$OUTPUT"

