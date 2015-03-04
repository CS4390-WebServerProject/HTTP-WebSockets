from datetime import datetime, time, tzinfo

##############################################################################################
# Author: Tim Gowan
# Date : Thu, 19 Feb 2015 18:19:43 CST 
# Description: 
#   a program that outputs the current day/time in HTTP Header format as the output using python native library.
# 
#   Sample Output with HTTP Header Format:           Thu, 19 Feb 2015 18:19:43 CST 
#
# Note: It will NOT determine timezones, defaults to 'CST' string (where the program was written and will be used)
###############################################################################################

def HTTPDate():
    # UTC is the same for GMT
    today = datetime.utcnow() # pull today's date from python native library
    year = str(today.year)
    
    # Create 3 char format for month 
    # Output string is in 'month' variable 
    m = today.month
    
    month = 'Def'
    if m == 1:
        month = 'Jan'
    elif m== 2:
        month = 'Feb'
    elif m== 3:
        month = 'Mar'
    elif m== 4:
        month = 'Apr'
    elif m== 5:
        month = 'May'
    elif m== 6:
        month = 'Jun'  
    elif m== 7:
        month = 'Jul'  
    elif m== 8:
        month = 'Aug'  
    elif m== 9:
        month = 'Sep'  
    elif m== 10:
        month = 'Oct'  
    elif m== 11:
        month = 'Nov'  
    elif m== 12:
        month = 'Dec'  
    
    # Create 2 char format for date
    # Output string is in 'day' variable
    day = ''
    if today.day <10:
        day = '0'  
    day += str(today.day)
    
    # Create 3 char format for day of the week
    # Output string is in 'dayOfWeek' variable
    w = datetime.weekday(today) # what day of the week, 0 is Monday, 6 is Sunday
    d = 'Def'
    if w == 0:
        dayOfWeek = 'Mon'
    elif w== 1:
        dayOfWeek = 'Tue'
    elif w== 2:
        dayOfWeek = 'Wed'
    elif w== 3:
        dayOfWeek = 'Thu'
    elif w== 4:
        dayOfWeek = 'Fri'
    elif w== 5:
        dayOfWeek = 'Sat'
    elif w== 6:
        dayOfWeek = 'Sun'    
        
        
    # Create 6 char format for time of the day  
    # Output string is in 'time' string variable 
    hour = ''
    if today.hour <10:
        hour = '0'  
    hour += str(today.hour)
    
    minute = ''
    if today.minute <10:
        minute = '0'  
    minute += str(today.minute)
    
    second = ''
    if today.second <10:
        second = '0'  
    second += str(today.second)
    
    time = ':'.join([hour,minute,second])
    
    # Assembling all fields into the HTTP format
    HTTPDateHeader = dayOfWeek + ', ' + ' '.join([day,month,year, time, 'GMT']) # Change 'CST' here to whichever timezone the code is being used
    return HTTPDateHeader