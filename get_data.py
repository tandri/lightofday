
# Fetch data from https://sunrise-sunset.org/

# Saves a table of times of sunrise, sunset, noon,
# and twilight beginnings and ends over one year.
# The table is organized in columns:
# (date | twilight_begin | sunrise | noon | sunset | twilight_end)
# The first column keeps datetime.date objects,
# and the other columns keep the time of the repsective events
# as the number of seconds from midnight (UTC) of the given date.

import pandas as pd
import urllib.request
import json
from datetime import datetime, timezone, timedelta

def as_datetime( datestring ):
    iso_8601_format = '%Y-%m-%dT%H:%M:%S%z'
    a_better_datestring = datestring[:22] + datestring[23:]
    utc_datetime = datetime.strptime( a_better_datestring, iso_8601_format )
    return utc_datetime


def is_leap_year( year ):
    last_day_of_february = (datetime(year,3,1) - timedelta(1)).day
    return last_day_of_february == 29



# -----------------------------------------
# ----------- CONFIG ----------------------
# -----------------------------------------

YEAR = 2018

# Reykjavik
PLACE_NAME = 'RVK'
LAT = 64.13
LNG = -21.82
TZ = timezone(timedelta(0))# not used


# # Lisbon
# PLACE_NAME = 'LIS'
# LAT = 38.72
# LNG = -9.14
# TZ = timezone(timedelta(0))# not used


# # Ponta Delgada
# PLACE_NAME = 'PDL'
# LAT = 37.74
# LNG = -25.68
# TZ = timezone(timedelta(hours=-1))# not used

# # Praia
# PLACE_NAME = 'PRA'
# LAT = 14.933
# LNG = -23.513
# TZ = timezone(timedelta(hours=-1))# not used

# # Husavik
# PLACE_NAME = 'HVK'
# LAT = 66.05
# LNG = -17.34
# TZ = timezone(timedelta(0))# not used


# # Tromso
# PLACE_NAME = 'TOS'
# LAT = 69.65
# LNG = 18.96
# TZ = timezone(timedelta(hours=1))# not used

# # Zurich
# PLACE_NAME = 'ZRH'
# LAT = 47.38
# LNG = 8.54
# TZ = timezone(timedelta(hours=1)) # not used


# # Moscow
# PLACE_NAME = 'MSK'
# LAT = 55.76
# LNG = 37.62
# TZ = timezone(timedelta(hours=3))# not used

# # Santiago, Chile
# PLACE_NAME = 'SCL'
# LAT = -33.45
# LNG = -70.67
# TZ = timezone(timedelta(hours=-5))# not used



FILE_NAME = PLACE_NAME+str(YEAR)+'.pkl'


# -----------------------------------------
# -----------------------------------------
# -----------------------------------------


# First entry for convenient indexing.
months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
month_days = [0,31,28+is_leap_year(YEAR),31,30,31,30,31,31,30,31,30,31]


data_table = pd.DataFrame()

print('Downloading data for %s (%.1f, %.1f) for %d' % (PLACE_NAME,LAT,LNG,YEAR))
for month in range(1,13):
    

    print( '\n\t' + months[month], end = '', flush = True )
    for day in range(1,1+month_days[month]):
        
        print( '.', end = '', flush = True )
        
        date_url = 'https://api.sunrise-sunset.org/json?lat=%f&lng=%f&date=%d-%d-%d&formatted=0' % (LAT,LNG,YEAR,month,day)
        with urllib.request.urlopen(date_url) as response:
            date_data = json.load(response)['results']
        
        ref = datetime( YEAR, month, day, 0, 0 ,0, 0, timezone.utc )

        date = ref.date()
        twilight_begin = ( as_datetime( date_data['civil_twilight_begin'] ) - ref ).total_seconds()
        sunrise = ( as_datetime( date_data['sunrise'] ) - ref ).total_seconds()
        noon = ( as_datetime( date_data['solar_noon'] ) - ref ).total_seconds()
        sunset = ( as_datetime( date_data['sunset'] ) - ref ).total_seconds()
        twilight_end = ( as_datetime( date_data['civil_twilight_end'] ) - ref ).total_seconds()
        
        table_row = [[ date, twilight_begin, sunrise, noon, sunset, twilight_end ]]
        
        data_table = data_table.append( table_row, ignore_index = True )

col_names = [ 'date', 'twilight_begin', 'sunrise', 'noon', 'sunset', 'twilight_end' ]
data_table.rename(columns = dict(zip(data_table.columns, col_names)), inplace = True)

print( '\nSaving to %s...' % FILE_NAME )
data_table.to_pickle(FILE_NAME)

