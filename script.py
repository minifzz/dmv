#!/usr/bin/env python3

from splinter import Browser
from dmv_lib import *
from datetime import datetime, timedelta

trying_account = 'min'
existing_account = 'yi'
existing_confirmation = 'TVGVV5'
existing_datetime = datetime.strptime("September 25 2020 14:30", "%B %d %Y %H:%M")

while True:
    print("Trying Acccount:{}, Existing Account: {}, Existing Confirmation: {}, Existing Appointment Time: {}".format(trying_account, existing_account, existing_confirmation, existing_datetime.strftime("%B %d %Y %H:%M"))) 
    new_appt = None
    startdate = datetime.today()
    # only schedule new appointment that is at least one day before the existing one
    enddate = datetime.fromordinal(existing_datetime.toordinal())
    while new_appt is None:
        ac = AppointmenChecker(trying_account, startdate, enddate)
        ac.startScheduleAppointment()
        #for office in PREFERED_OFFICES:
        for office in ['Everett']:
            new_appt = ac.tryMakeAnAppointment(office)
        ac.close()
   
    print("Cancel appointment {} {}".format(existing_account, existing_confirmation))
    # cancel the other appointment 
    ac = AppointmenChecker(existing_account)
    ac.cancelAppointment(existing_confirmation)

    existing_account, trying_account = trying_account, existing_account
    _, existing_datetime, existing_confirmation = new_appt
    ac.close()
        
