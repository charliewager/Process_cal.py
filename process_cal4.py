#!/usr/bin/env python3

import re
import datetime

'''
This package contains the process_cal and event classes, both of these are immutable objects. 
This package lets the user interact with ics files to produce human readable output of events on a given day 

This package contains the folllowing functions to aid the methods of the process_cal class:
read-file
create_repeating
increment_event
create_datetime
extract_date_time
sort_list
create_print_string
format_event
format_time
'''

class process_cal:
    '''
    This class contains two methods, the __init__ constructer and the get_events_for_day method. 
    This class is immutable, i.e. once the data has been set by the constructer it cannot be changed without creating another instance
    '''

    def __init__(self, filename):
        '''
        This method takes a string containing a file name as a parameter then the method reads the file, creates a sorted list of 
        the events found in the file, and then assigns this list to the event_list field of self.
        '''
        file_to_read = open(filename);

        unsorted_list = read_file(file_to_read)
        self.event_list = sort_list(unsorted_list)

        file_to_read.close()

    def get_events_for_day(self, day):
        '''
        This method takes a datetime object as a parameter and returns a formatted string containing the events that occur on the day
        specified by the datetime parameter
        '''
        return_string = ""
        daymatch_count = 0
        for i, event in enumerate(self.event_list):

            curr_day = event.date
            if curr_day == day:
                daymatch_count += 1

                if daymatch_count == 1:
                    return_string += create_print_string(event)
                else:
                    return_string += create_print_string(event, 0)

                try:
                    if self.event_list[(i + 1)].date == day:
                        return_string += '\n'
                except:
                    break

        if return_string:
            return return_string
        else:
            return None

class event: 
    '''
    This class contains a single method, the __init__ contructor method.
    This class is immutable meaning once the data is set it cannot be changed without creating a new instance of the class
    '''
    def __init__(self, startdt, end_dt, location, summary, date=None):
        '''This method takes the datetime objects startdt, end_dt, location, summary and date and assigns them to the appropriate fields of self'''
        
        self.startdt = startdt
        self.end_dt = end_dt
        self.location = location
        self.summary = summary
        self.date = date

def read_file(file):
    '''
    This function takes a file object, reads it, creates a list of events found in the file and returns said list
    Parameters: file: an open file object
    Returns: event_list (list): a list of events
    '''
    for line in file:

        avoid_n = len(line) - 1
        if re.match(r'BEGIN:VCALENDAR', line) is not None:

            event_list = []

        elif re.match(r'BEGIN:VEVENT', line) is not None:

            start = ""
            end = ""
            location = ""
            summary = ""
            repeating = 0
            repeat_until = ""

        if re.match(r'DTSTART:', line) is not None:

            start = line[8:avoid_n]

        elif re.match(r'DTEND:', line) is not None:

            end = line[6:avoid_n]

        elif re.match(r'LOCATION:', line) is not None:

            location = line[9:avoid_n]

        elif re.match(r'SUMMARY:', line) is not None:

            summary = line[8:avoid_n]

        elif re.match(r'RRULE:', line) is not None:

            repeating = 1
            match_list = re.findall('UNTIL=(.*);', line)
            repeat_until = create_datetime(match_list[0], 0)

        elif re.match(r'END:VEVENT', line) is not None:

            date = create_datetime(start, 1)
            startdt = create_datetime(start, 0)
            end_dt = create_datetime(end, 0)
            new_event = event(startdt, end_dt, location, summary, date)
            event_list.append(new_event)

            if repeating == 1:
                create_repeating(event_list, new_event, repeat_until)

        elif re.match(r'END:VCALENDAR', line) is not None:

            return event_list

def create_repeating(event_list, orig_event, limit):
    '''
    This function takes a repeating event, creates all required repetitions and adds them to the event list.
    These repetitions are a week apart.
    Parameters: event_list (list): the list that the repetitions are to be added to
                orig_event (event): an event object to be incremented to create the repititions
                limit (datetime): the datetime object specifying when the repetitions should end
    Returns: Nothing 
    '''    
    increment = datetime.timedelta(7)
    next_event = increment_event(orig_event, increment)
    while next_event.startdt < limit:
        event_list.append(next_event)
        next_event = increment_event(next_event, increment)

def increment_event(old_event, increment):
    '''
    This function increments an event by the amount specified by the increment parameter
    Parameter: old_event (event): the event to be incremented
               increment (datetime): the amount to increment the event by
    Returns: an event object that is an incremented version of the parameter event
    '''
    new_date = old_event.date + increment
    new_start = old_event.startdt + increment
    new_end = old_event.end_dt + increment
    return event(new_start, new_end, old_event.location, old_event.summary, new_date)

def create_datetime(dtstring, date_only):
    '''
    This function creates a datetime object
    Parameters: dtstring (string): the dt from the ics file 
                date_only (int): should be either 0 or 1, tells the function wether to include the time as well as the date
    Returns: the datetime object created from dtstring
    '''
    date = extract_date_time(dtstring, 1)
    if date_only == 1:
        return datetime.datetime(date[0], date[1], date[2])
    else:
        return datetime.datetime(date[0], date[1], date[2], date[3], date[4])

def extract_date_time(dtstring, asInt):
    '''
    This function extracts the year, month, date, hour and minute from a dtstring
    Parameters: dtstring (string): the dt from the ics file
                asInt (int): must be 0 or 1, determines if the values in the return list should be ints or strings
    Returns: date (list): a list containing the year, month, day, hour, and minute from the dtstring. Indexes are as follows,
                          0:year 1:month 2:day 3:hour 4:minute
    '''
    date = []
    if asInt == 1:
        date.append(int(dtstring[:4]))
        date.append(int(dtstring[4:6]))
        date.append(int(dtstring[6:8]))
        date.append(int(dtstring[9:11]))
        date.append(int(dtstring[11:13]))
    else:
        date.append(dtstring[:4])
        date.append(dtstring[4:6])
        date.append(dtstring[6:8])
        date.append(dtstring[9:11])
        date.append(dtstring[11:13])

    return date

def sort_list(rawlist):
    '''
    This function sorts a list via a bubble sort algorithm 
    Parameters: rawlist (list): the list to be sorted 
    Returns: rawlist (list): the newly sorted list
    '''
    for item in range(len(rawlist)):
        for compare in range(len(rawlist)):

            if rawlist[compare].startdt > rawlist[item].startdt:
                temp = rawlist[item]
                rawlist[item] = rawlist[compare]
                rawlist[compare] = temp

    return rawlist

def create_print_string(event, withdate=1):
    '''
    This function, given an event, creates a formatted string to be printed
    Parameters: event (event): the event containing the data to be formatted into a human-readable string
                withdate (int): 0 or 1. determines wether the string contains the date heading or just the info for the event
    Returns: string: a string containing either the full date and info-line or just the info-line
    '''
    formatted_event = format_event(event)
    info_line = formatted_event.startdt + " to " + formatted_event.end_dt + ": " + formatted_event.summary + " {{" + formatted_event.location + "}}"

    if withdate == 1:
        for i in range(len(formatted_event.date)):
            if i == 0:
                dashes = "-"
            else:
                dashes += "-"

        return formatted_event.date + "\n" + dashes + "\n" + info_line

    else:
        return info_line

def format_event(raw_event):
    '''
    This function formats a given events information into a human readable format
    Parameter: raw_event (event): the event object containing the data to be formatted
    Returns: event: a new event object containing the human-readable form of the data form the parameter
    '''
    date = raw_event.startdt.strftime("%B %d, %Y (%a)")
    start_time = format_time(raw_event.startdt)
    end_time = format_time(raw_event.end_dt)
    return event(start_time, end_time, raw_event.location, raw_event.summary, date)

def format_time(rawdt):
    '''
    This function creates a human-readable format of a datetime object
    Parameter: rawdt (datetime): a datetime object to be formatted
    Returns: formatted (string): a human-readable format of the given datetime
    '''
    formatted = rawdt.strftime("%I:%M %p")
    if formatted[0] == '0':
        return " " + (formatted[1:])
    else:
        return formatted
