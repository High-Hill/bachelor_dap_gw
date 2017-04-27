#!/bin/sh

while :
    do
        sleep 1s
        tail -n 1000 /var/log/kern.log | sed 's/  / /g' | grep -e "`date +"%b %-d %H:%M:%S"`" | grep "FORWARD_F" > tmp.txt
        python packet_counter_pipe.py tmp.txt
    done
