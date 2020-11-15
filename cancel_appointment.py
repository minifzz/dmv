#!/usr/bin/env python3

from splinter import Browser
from dmv_lib import *
from datetime import datetime, timedelta
import sys

if __name__ == "__main__":
    account = sys.argv[1]
    confirmation = sys.argv[2]
    print("Cancel appointment {} {}".format(account, confirmation))
    # cancel the other appointment 
    ac = AppointmenChecker(account) 
    ac.cancelAppointment(confirmation)
    ac.close()
