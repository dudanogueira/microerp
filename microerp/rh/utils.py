import datetime, urllib2
from icalendar import Calendar

def get_weeks_old(now=datetime.date.today(), weeks=5):
    numweeks = weeks
    weeks = []
    now = now - datetime.timedelta(days=now.weekday())
    offset = datetime.timedelta(days=-1)
    for week in range(numweeks):
       this_week = []
       for day in range(7):
            date = now + offset
            this_week.append( date )
            offset += datetime.timedelta(days=1)
       weeks.append(this_week)
    return weeks    
        
def get_weeks(now=datetime.date.today(), weeks=5, first_week_day=6):
    # segunda,  terca, quarta, quinta, sexta, sabado, domingo
    #       0,      1,      2,      3,     4,      5,       6
    #      -1,     -2,     -3,     -4,     -5,    -6,       0
    offsets = (-1, -2, -3, -4, -5, -6, 0)
    numweeks = weeks
    weekday = now.weekday()
    first_day = now + datetime.timedelta(offsets[weekday])
    print "first day", first_day
    offset=0
    output = []
    for week in range(numweeks):
        this_week = []
        for day in range(7):
            date = first_day+ datetime.timedelta(offset)
            offset += 1
            this_week.append( date )
        output.append(this_week)
    return output

def get_last_whole_week(today=None, epoch=False):
    # a date object
    date_today = today or datetime.date.today()
    print "date_today: ", date_today
 
    # By default day 0 is Monday. Sunday is 6.
    dow_today = date_today.weekday()
    print "dow_today: ", dow_today
 
    if dow_today == 6:
        days_ago_saturday = 1
    else:
        # If day between 0-5, to get last saturday, we need to go to day 0 (Monday), then two more days.
        days_ago_saturday = dow_today + 2
    print "days_ago_saturday: ", days_ago_saturday
    # Make a timedelta object so we can do date arithmetic.
    delta_saturday = datetime.timedelta(days=days_ago_saturday)
    print "delta_saturday: ", delta_saturday
    # saturday is now a date object representing last saturday
    saturday = date_today - delta_saturday
    print "saturday: ", saturday
    # timedelta object representing '6 days'...
    delta_prevsunday = datetime.timedelta(days=6)
    # Making a date object. Subtract the 6 days from saturday to get "the Sunday before that".
    prev_sunday = saturday - delta_prevsunday
 
    # we need to return a range starting with midnight on a Sunday, and ending w/ 23:59:59 on the
    # following Saturday... optionally in epoch format.
 
    if epoch:
        # saturday is date obj = 'midnight saturday'. We want the last second of the day, not the first.
        saturday_epoch = time.mktime(saturday.timetuple()) + 86399
        prev_sunday_epoch = time.mktime(prev_sunday.timetuple())
        last_week = (prev_sunday_epoch, saturday_epoch)
    else:
        saturday_str = saturday.strftime('%Y-%m-%d')
        prev_sunday_str = prev_sunday.strftime('%Y-%m-%d')
        last_week = (prev_sunday_str, saturday_str)
    return last_week


