import splinter
from splinter import Browser
from shutil import move
import re
import time
import selenium
from datetime import datetime, date
from twilio.rest import Client

# Your Twilio Account Sid and Auth Token from twilio.com/console
account_sid = ""
auth_token = ""

# Your dmv accounts, you will need to two to use alternatively
# between checking a better apointment time and holding an spot
# 
account1 = ("account1", "username", "password", "email", "phone")
account2 = ("account2", "username", "password", "email", "phone")

def send_message(message):
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
            body=message,
            from_="", #your twilio number
            to="" # your phone number
        )

OFFICES = [
 'Anacortes',
 'Bellingham',
 'Bremerton',
 'Centralia',
 'Clarkston',
 'Colville',
 'Ellensburg',
 'Everett',
 'Federal Way',
 'Hoquiam',
 'Ilwaco',
 'Kelso',
 'Kennewick',
 'Kent',
 'Lacey',
 'Lynnwood',
 'Moses Lake',
 'Mount Vernon',
 'Oak Harbor',
 'Omak',
 'Parkland',
 'Port Angeles',
 'Port Townsend',
 'Poulsbo',
 'Pullman',
 'Puyallup',
 'Renton',
 'Seattle-Downtown',
 'Seattle-West',
 'Shoreline',
 'Smokey Point',
 'Spokane',
 'Spokane Valley',
 'Tacoma',
 'Union Gap',
 'Vancouver East',
 'Vancouver North',
 'Wenatchee',
 'White Salmon']

PREFERED_OFFICES = [
'Lynnwood',
'Shoreline',
'Seattle-Downtown', 
'Seattle-West', 
'Renton', 
'Kent', 
'Everett',
'Federal Way',
'Tacoma',
 'Smokey Point',
'Puyallup',
'Parkland',
 'Mount Vernon',
 ]

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
WEEKENDS = ['Saturday', 'Sunday']

def select_option(b, select_name, option_name):
    b.find_by_id(select_name).click()
    b.find_option_by_value(option_name).click()

def select_option_by_text(b, select_name, option_text):
    b.find_by_id(select_name).click()
    b.find_option_by_text(option_text).click()

def filterAppts(appts, start_date=None, end_date=None, only_weekends=False):
    appts = {id: datetime.strptime("2020 " + datetimestr, '%Y %A %B %d %I:%M %p')
            for id, datetimestr in appts}
    
    if start_date is not None:
        appts = {id: dt for id, dt in appts.items() if dt >= start_date}
    if end_date is not None:
        appts = {id: dt for id, dt in appts.items() if dt <= end_date}
    if only_weekends:
        appts = {id: dt for id, dt in appts.items() if not dt.weekday()}
    return appts.items()

def findBestAppointment(appts):
    # return the appointment with earliest date but latest time
    def sort_fun(appt):
        appt_dt = appt[1]
        appt_date = datetime.fromordinal(appt_dt.toordinal())
        appt_time = (appt_dt - appt_date).total_seconds()
        return appt_date, -appt_time

    return sorted(appts, key=sort_fun)[0]

class AppointmenChecker:
    def __init__(self, account, startdate=None, enddate=None):
        self.account = account
        if account == account1[0]:
            account_details = account1[1:]
        elif account == accont2[0]:
            account_details = account2[1:]
        else:
            raise Exception("Invalid account {}".format(account))
    
        self.username, self.password, self.email, self.phone = account_details
        
        self.startdate = startdate
        self.enddate = enddate
        self.only_weekends = False
        self.b = Browser("chrome")
        self.login()

    # helper functions
    def click_with_retry(self, id):
        try:
            self.b.find_by_id(id).click()
        except:
            time.sleep(0.5)
            self.b.find_by_id(id).click()
    
    def click_by_text_with_retry(self, text):
        try:
            self.b.find_by_text(text).click()
        except:
            time.sleep(0.5)
            self.b.find_by_text(text).click()
    
    def fill_with_retry(self, id, content):
        try:
            self.b.find_by_id(id).fill(content)
        except:
            time.sleep(0.5)
            self.b.find_by_id(id).fill(content)
    
    def select_with_retry(self, id, option):
        try:
            self.b.find_by_id(id).click()
            self.b.find_option_by_text(option).click()
        except:
            time.sleep(0.5)
            self.b.find_by_id(id).click()
            self.b.find_option_by_text(option).click()

    def next(self):
        self.click_with_retry('d-__NextStep')

    def login(self):
        self.b.visit('https://secure.dol.wa.gov/home')
        try:
            #b.fill('username', 'mzhang94')
            self.b.fill('username', self.username)
        except Exception:
            self.b.reload()
            self.b.fill('username', self.username)
        self.b.fill('password', self.password)
        self.click_with_retry('btnLogin')
        self.click_with_retry('l_k-v-4')
        
    
    def loadOffice(self, office):
        self.next()
        
        self.select_with_retry('d-l1', "Get a license/Id")
        self.select_with_retry('d-m1', 'Personal Driver License')
        self.next()
        
        self.next()
        
        time.sleep(0.300) # wait for 0.3 second
        self.fill_with_retry('d-w2', self.email)
        self.fill_with_retry('d-x2', self.email)
        self.fill_with_retry('d-03', self.phone)
        self.next()

        select_option(self.b, 'd-93', 'No')
        self.next()

        self.select_with_retry('d-14', office)
        self.click_with_retry('d-24')
    
    def findAvailableAppointments(self):
        appts = []
        if self.b.find_by_id('caption2_c-z').first.value != "":
            return []
        
        elements = self.b.driver.find_elements_by_class_name("DocFieldLink")
        for e in elements:
            id = e.get_attribute("id")
            time = e.text
            if 'AM' not in time and 'PM' not in time:
                continue
            header_id = "c-{}-CH".format(id.split("-")[1])
            date = self.b.find_by_id(header_id).value 
            appts.append((id, date.replace("\n", " ") + " " + time))
        return sorted(appts)
    
    def returnToStartPage(self):
        self.b.find_by_text("Cancel")[1].click()
    
    def startScheduleAppointment(self):
        self.click_with_retry('d-i')
    
    def makeAppointment(self, appt, office):
        appt_id, appt_time = appt
        self.click_with_retry(appt_id)
        time.sleep(0.3)
        self.b.find_by_text('Confirm')[1].click()
        time.sleep(0.3)
        confirmation_code = self.b.find_by_id('caption2_c-a2').text.split('\n')[0].split()[-1]
        message = "Booked appointment at office {} on {} with account {}. Confirmation code: {}"\
                .format(office, 
                    datetime.strftime(appt_time, "%A %m/%d/%Y %H:%M:%S"),
                    self.account, 
                    confirmation_code)
        print(message)
        send_message(message)
        return confirmation_code
        
    def tryMakeAnAppointment(self, office):
        self.loadOffice(office)
        appts = self.findAvailableAppointments()
        appts = filterAppts(appts, self.startdate, self.enddate, self.only_weekends)
        if len(appts) > 0:
            appt = findBestAppointment(appts)
            confirmation_code = self.makeAppointment(appt, office)
            return office, appt, confirmation_code
        else:
            self.returnToStartPage()
            return None
    
    def cancelAppointment(self, confirmation_code):
        self.click_by_text_with_retry('Cancel an appointment')
        self.click_by_text_with_retry('I know my code')
        self.fill_with_retry('d-7', confirmation_code)
        self.fill_with_retry('d-9', self.email)
        self.click_with_retry('d-j') # Find my appointment
        
        self.click_with_retry('d-k') # 
        
        self.click_with_retry('c-l') # Cancel appointment

        self.click_by_text_with_retry('Yes') # Yes

    def close(self):
        self.b.quit()


"""
for office in PREFERED_OFFICES:
    if ac.tryMakeAnAppointment(office):
        break
"""
