#!/usr/bin/env python3

from splinter import Browser
from dmv_lib import *
from datetime import datetime, timedelta
import sys

offices_to_check = [
'Lynnwood',
'Shoreline',
'Seattle-Downtown', 
'Seattle-West', 
'Renton', 
'Kent', 
'Everett',
 ]

if __name__ == "__main__":
    account = sys.argv[1]
    
    startdate = datetime.today()
    # only schedule new appointment that is at least one day before the existing one
    enddate = datetime.today() + timedelta(days=7)
    finish = False
    while not finish:
        try:
            ac = AppointmenChecker(account, startdate, enddate)
            ac.startScheduleAppointment()
            #for office in PREFERED_OFFICES:
            for office in offices_to_check:
                if ac.tryMakeAnAppointment(office):
                    finish = True
                    break
            ac.close()
        except Exception as e:
            continue
