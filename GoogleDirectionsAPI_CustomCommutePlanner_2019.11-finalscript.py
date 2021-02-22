# NOTE: THIS SCRIPT WAS LAST WRITTEN WITH PYTHON 2.7 AND UPDATED IN DECEMBER 2019.
# AS OF FEB 2021, THIS SCRIPT WILL NOT WORK WITH THE LATEST VERSION OF GOOGLE DIRECTIONS API DUE TO CHANGES IN THE JSON OUTPPUT.
# THE CUSTOM GUI (TKINTER) INTERFACE STILL WORKS AND A SUCCESSFUL QUERY WILL BE MADE TO THE GOOGLE DIRECTIONS API,
# HOWEVER, THE SCRIPT WILL FAIL WHEN IT ATTEMPTS TO PRINT THE RESULTS OF THE QUERY TO THE CONSOLE AND USER'S DESKTOP.
# DO NOT RELY ON THIS SCRIPT UNTIL UPDATES/FIXES HAVE BEEN MADE TO IT!!! (DATE TBD)

# REQUIRES      : GOOGLE DIRECTIONS API KEY
# HOW IT WORKS  : RUN THE CODE, A CUSTOM GUI WILL POP UP, FILL IN "START LOCATION", "END LOCATION", "ARRIVAL TIME", "API KEY", AND "OUTPUT FILE NAME"
# DOCUMENTATION : https://github.com/SharonWHLing/custom_commute_planner/blob/main/GoogleDirectionsAPI_CustomCommutePlanner_2019.11-pdf.pdf
#############################################################

# Step 1: import all necessary Python packages

import pendulum, tinyurl # install via pip method if unable to import directly through Pyscripter
import Tkinter as Tk
from Tkinter import *
import os, sys, json, time, urllib
from urllib import urlencode
import collections
from collections import OrderedDict # this keeps the order of the 'dictionary' especially when submitting URLs

# Step 2: setup a custom user interface created with Tkinter
# User inputs desired Start Address, End Address, Arrive By [hour (HH), minute (MM), time of day (AM/PM)], API Key, and Output File Name into custom user interface
# User input values are collected and carried over to Step 3

root = Tk()
root.title("Custom Commute Planner v 1.0")

# set "Start Address" entry in custom user interface
Label(root, text = "Start Address          :").grid(row = 0, sticky = W)
startadd = Entry(root, width = 30)
startadd.grid(row = 0, column = 1, columnspan = 3, sticky = W)

# set "End Address" entry in custom user interface
Label(root, text = "End Address           :").grid(row = 1, sticky = W)
endadd = Entry(root, width = 30)
endadd.grid(row = 1, column = 1, columnspan = 3, sticky = W)

# set "Arrive By" entries in custom user interface
Label(root, text = "Arrive By                 :").grid(row = 2, sticky = W)

# set "Arrive By" hour (HH) value in custom user interface
hh_options = [1,2,3,4,5,6,7,8,9,10,11,12]
hh = StringVar(root)
hh.set(hh_options[0]) # default value

a = OptionMenu(root, hh, *hh_options)
a.grid(row = 2, column = 1, sticky = W)

# set "Arrive By" minute (MM) value in custom user interface
mm_options = ["00","15","30","45"]
mm = StringVar(root)
mm.set(mm_options[0]) # default value

b = OptionMenu(root, mm, *mm_options)
b.grid(row = 2, column = 2, sticky = W)

# set "Arrive by" time of day (AM/PM) value in custom user interface
ampm_options = ["am","pm"]
ampm = StringVar(root)
ampm.set(ampm_options[0]) # default value

c = OptionMenu(root, ampm, *ampm_options)
c.grid(row = 2, column = 3, sticky = W)

# set "API Key" entry in custom user interface
Label(root, text = "API Key                   :").grid(row = 4, sticky = W)
apikey = Entry(root, width = 30)
apikey.grid(row = 4, column = 1, columnspan = 3, sticky = W)

# set "Output File Name" entry in custom user interface
Label(root, text = "Output File Name :").grid(row = 5, sticky = W)
OutputName = Entry(root, width = 30)
OutputName.grid(row = 5, column = 1, columnspan = 3, sticky = W)

# Step 3: gather user input values for further action

def getInput():

    start = startadd.get()
    end = endadd.get()
    HH = hh.get()
    MM = mm.get()
    AMPM = ampm.get()
    API_KEY = apikey.get()
    OUTPUT_NAME = OutputName.get()
    root.destroy() #closes custom user interface after Submit button is clicked

    global UserInput
    UserInput = [start, end, HH, MM, AMPM, API_KEY, OUTPUT_NAME] #collects user input into a list

Button(root, text="Submit", command=getInput).grid(row = 6, column = 1)

mainloop()

# assign labels for user input values
start = UserInput[0]
end = UserInput[1]
HH = UserInput[2]
MM = UserInput[3]
AMPM = UserInput[4]
API_KEY = UserInput[5]
OUTPUT_NAME = UserInput[6]

# create a class that will print output to both the console and a file (on the user's desktop)
# source: https://stackoverflow.com/questions/24204898/python-output-on-both-console-and-file/24206109#24206109

desktop = os.path.expanduser("~\Desktop") # set user's desktop as output path

class Printer:
    def __init__(self, filename):
        self.out_file = open(filename, "w")
        self.old_stdout = sys.stdout
        #this object will take over stdout's job
        sys.stdout = self
    #executed when the user does a 'print'
    def write(self, text):
        self.old_stdout.write(text)
        self.out_file.write(text)
    #executed when 'with' block begins
    def __enter__(self):
        return self
    #executed when 'with' block ends
    def __exit__(self, type, value, traceback):
        #we don't want to log anymore. Restore the original stdout object.
        sys.stdout = self.old_stdout

# Step 4: print user input to both the console and a file (on the user's desktop)

with Printer(desktop+"\\"+OUTPUT_NAME+".txt"):
    print "USER INPUT       :"
    print
    print "Start Address    : " + start
    print "End Address      : " + end
    print "Arrive By        : " + str(HH) + ":" + str(MM) + AMPM
    print

# Step 5: send user input values to json/Google Maps

    if HH == "12" and AMPM == "am": # effectively convert HH entries that are 12:00am to 00:00 am
        HH = 0

    if HH != "12" and AMPM == "pm": # effectively convert HH entries that are PM to 24-hour time i.e. 1:00pm = 13:00
        HH = int(HH)+12
    else:
        HH = int(HH)

# convert HH, MM and AM/PM user input to UTC values for json / GoogleMaps submission
# pendulum.today() returns today's date with HH & MM automatically set at 00:00; so user input of HH & MM time is added to that
    dt = pendulum.today().add(hours=int(HH)).add(minutes=int(MM))
    dt = int(dt.timestamp())

# generate json submission url for general inquiry
    jsonurl_prefix = 'https://maps.googleapis.com/maps/api/directions/json?'
    jsonurl_data = urllib.urlencode(OrderedDict([("origin", start), ("destination", end), ("arrival_time", str(dt)), ("mode","transit"), ("key", API_KEY)]))
    jsonurl = jsonurl_prefix+jsonurl_data
    jsonurl_gresp = urllib.urlopen(jsonurl)
    jsonurl_jresp = json.loads(jsonurl_gresp.read())
    jsonurl_url = tinyurl.create_one(jsonurl)

# generate a unique GoogleMaps map link for that individual segment
# unfortunately, the link defaults to "depart now" and departure/arrival times can't be set -- this seems to be a Google Maps quirk
    gmapsurl_prefix = 'https://www.google.com/maps/dir/?api=1&'
    gmapsurl_data = urllib.urlencode(OrderedDict([("origin", start), ("destination", end), ("travelmode", "transit")]))
    gmapsurl = gmapsurl_prefix+gmapsurl_data
    gmapsurl_url = tinyurl.create_one(gmapsurl)

# generate latlong submission url for latlong inquiry --- the latlong details are called upon further down the code
    latlngurl_prefix = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='

# Step 6: print output to both the console and a file (on the user's desktop)

    print "SUMMARY OUTPUT   :"
    print
    print "Google Maps URL  :", gmapsurl_url
    print "JSON URL         :", jsonurl_url
    print "Total Distance   :", jsonurl_jresp['routes'][0]['legs'][0]['distance']['text']
    print "Total Duration   :", jsonurl_jresp['routes'][0]['legs'][0]['duration']['text']
    print "Departure Time   :", jsonurl_jresp['routes'][0]['legs'][0]['departure_time']['text']
    print "Arrival Time     :", jsonurl_jresp['routes'][0]['legs'][0]['arrival_time']['text']
    print
    print "DIRECTIONS       :"

    for i in range (0, len (jsonurl_jresp['routes'][0]['legs'][0]['steps'])):
        time.sleep(.1)
        i_ins = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['html_instructions'] # sometimes can be gibberish so supplement with proper From/To details
        i_mod = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['travel_mode']
        i_dis = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['distance']['text']
        i_dur = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['duration']['text']
        print
        print('Trip Segment {0}'.format(i+1)), "  :", i_ins
        print "Travel Mode      : " + i_mod.title()

# print From/To details for individual segments of the trip
# note: this is tricky because of how Google Maps' json output is generated even when submitting an overall transit-based query:
    # 1) if a trip segment is identified as "transit", the json output includes a ['departure stop'] and ['arrival stop'] address string
    # 2) but if a trip segment is identified as non-transit i.e. walking, the json output only provides lat/longs of the start/end location
    # 3) so for a non-transit trip segment, to produce a departure/arrival stop address as json output, a reverse geocoding query must be submitted
        # since the first segment of the overall trip is likely non-transit i.e. walk from home to bus stop,
        # check that "transit_details" are NOT in the json output and then proceed to the reverse geocoding query to create From/To details
        if "transit_details" not in jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]:
            i_start_lat = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['start_location']['lat']
            i_start_lng = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['start_location']['lng']
            i_start_latlngurl = latlngurl_prefix+str(i_start_lat)+","+str(i_start_lng)+"&key="+API_KEY
            i_start_latlngurl_gresp = urllib.urlopen(i_start_latlngurl)
            i_start_latlngurl_jresp = json.loads(i_start_latlngurl_gresp.read())
            i_start = i_start_latlngurl_jresp['results'][0]['formatted_address']
            print "From             :", i_start
            i_end_lat   = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['end_location']['lat']
            i_end_lng   = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['end_location']['lng']
            i_end_latlngurl = latlngurl_prefix+str(i_end_lat)+","+str(i_end_lng)+"&key="+API_KEY
            i_end_latlngurl_gresp = urllib.urlopen(i_end_latlngurl)
            i_end_latlngurl_jresp = json.loads(i_end_latlngurl_gresp.read())
            i_end = i_end_latlngurl_jresp['results'][0]['formatted_address']
            print "To               :", i_end
        # generate a unique GoogleMaps map link for that individual segment
        # unfortunately, the link's departure/arrival times can't be set -- this seems to be a Google Maps quirk
            gmapsurl_data = urllib.urlencode(OrderedDict([("origin", i_start), ("destination", i_end), ("travelmode", i_mod.lower())]))
            gmapsurl = gmapsurl_prefix+gmapsurl_data
            gmapsurl_url = tinyurl.create_one(gmapsurl)
            print "Google Maps URL  : " + gmapsurl_url
        # alternatively, if the segment IS identified as transit, retrieve ['departure stop'] and ['arrival stop'] address strings for From/To details:
        if "transit_details" in jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]:
            i_start = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['transit_details']['departure_stop']['name']
            print "From             : " + i_start
            i_end = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['transit_details']['arrival_stop']['name']
            print "To               : " + i_end
        # generate a unique GoogleMaps map link for that individual segment
        # unfortunately, the link defaults to "depart now" and departure/arrival times can't be set -- this seems to be a Google Maps quirk
            gmapsurl_data = urllib.urlencode(OrderedDict([("origin", i_start), ("destination", i_end), ("travelmode", i_mod.lower())]))
            gmapsurl = gmapsurl_prefix+gmapsurl_data
            gmapsurl_url = tinyurl.create_one(gmapsurl)
            print "Google Maps URL  : " + gmapsurl_url
        print "Distance         : " + i_dis
        print "Duration         : " + i_dur

# print Departure Time & Arrival Time details for individual segments of the trip
# note: this is tricky because of how Google Maps' json output is generated even when submitting an overall transit-based query:
    # 1) if a trip segment is identified as "transit", the json output includes a ['departure time'] and ['arrival time'] string
    # 2) but if a trip segment is identified as non-transit i.e. walking, the json output does not contain this information
    # 3) so for a non-transit trip segment, to produce departure time & arrival time output, these values must often be calculated manually
    # 4) we can also assume that for individual non-transit trip segments,
        # a) where i = 0 (aka 1st trip segment), departure time = departure time of overall trip & arrival time = departure time of next trip segment
        # b) where i > 0 (aka 2nd or more trip segment), departure time = arrival time of previous trip segment & arrival time = departure time of next trip segment
        # c) arrival time = departure time + duration of trip segment (which IS produced as json output)
        # this leads to the following code:
        # where i = 0 (aka 1st trip segment)
        if i == 0:
            print "Departure Time   : " + jsonurl_jresp['routes'][0]['legs'][0]['departure_time']['text']
            i_arr = (jsonurl_jresp['routes'][0]['legs'][0]['departure_time']['value']) + (jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['duration']['value'])
            i_arr = pendulum.from_timestamp(i_arr, tz='local')
            i_arr = i_arr.to_day_datetime_string()
            i_arr = str(i_arr).split()
            print "Arrival Time     : " + i_arr[4] + i_arr[5].lower()
        # where i > 0 (aka 2nd or more trip segment)
        if i is not 0 and jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['travel_mode'] == "WALKING":
            print "Departure Time   : " + jsonurl_jresp['routes'][0]['legs'][0]['steps'][i-1]['transit_details']['arrival_time']['text']
            i_arr = (jsonurl_jresp['routes'][0]['legs'][0]['steps'][i-1]['transit_details']['arrival_time']['value']) + (jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['duration']['value'])
            i_arr = pendulum.from_timestamp(i_arr, tz='local')
            i_arr = i_arr.to_day_datetime_string()
            i_arr = str(i_arr).split()
            print "Arrival Time     : " + i_arr[4] + i_arr[5].lower()
        # where the individual trip segment is identified as "transit"
        if "transit_details" in jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]:
            i_dep = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['transit_details']['departure_time']['text']
            print "Departure Time   : " + i_dep
            i_arr = jsonurl_jresp['routes'][0]['legs'][0]['steps'][i]['transit_details']['arrival_time']['text']
            print "Arrival Time     : " + i_arr
    print
    print "Thank you for using this Custom Commute Planner v 1.0!"
