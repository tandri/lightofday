
import os

import numpy as np
import matplotlib.pyplot as plt
from datetime import date, time
import pandas as pd

from sunny_mornings import make_sunny_morning_plot
from hours_of_daylight import make_daylight_hours_plot, make_daylight_hours_comparison_plot
from sunshine_carpet import make_sunshine_carpet_plot

# -----------------------------------------
# ----------- CONFIG ----------------------
# -----------------------------------------

LOC = 'RVK'
LOCNAME = r' í Reykjavík'
# Offset in hours from UTC in winter.
UTC_OFFSET = -1


# LOC = 'PDL'
# LOCNAME = r' í Ponta Delgada'
# # Offset in hours from UTC in winter.
# UTC_OFFSET = -1

# LOC = 'PRA'
# LOCNAME = r' í Praia'
# # Offset in hours from UTC in winter.
# UTC_OFFSET = -1


# LOC = 'HVK'
# LOCNAME = r' á Húsavík'
# # Offset in hours from UTC in winter.
# UTC_OFFSET = -1

# LOC = 'TOS'
# LOCNAME = r' í Tromsø'
# # Offset in hours from UTC in winter.
# UTC_OFFSET = 1

# LOC = 'MSK'
# LOCNAME = r' í Moskvu'
# # Offset in hours from UTC in winter.
# UTC_OFFSET = 3

# LOC = 'SCL'
# LOCNAME = r' í Santiago'
# # Offset in hours from UTC in winter.
# UTC_OFFSET = -5


YEAR = 2018
DATA_PATH = '%s%d.pkl' %(LOC,YEAR)



# In 2018, DST starts on March 25 and ends October 28
DST_START_DATE = date(YEAR,3,25)
DST_END_DATE = date(YEAR,10,28)


plt.rc('font', family='Times New Roman')
DPI = 150

DAY_COLOR = '#c6e5ff'
TWI_COLOR = '#106ebc'

NIGHT_COLOR = '#033e70'

BACKGROUND_COLOR = '#eaeeff'

NOON_COLOR = '#ffd923'
SLEEP_COLOR = '#1ea050'




daylight_hours_colors = [DAY_COLOR, TWI_COLOR]
sunny_mornings_colors = [DAY_COLOR, TWI_COLOR, BACKGROUND_COLOR]
sunshine_carpet_colors = [DAY_COLOR, TWI_COLOR, NIGHT_COLOR, NOON_COLOR, SLEEP_COLOR]


# -----------------------------------------
# ------------- LOAD DATA -----------------
# -----------------------------------------
print('Loading %s' % DATA_PATH)

utc_data = pd.read_pickle(DATA_PATH)

dates = utc_data['date']


# Move the data from UTC to local time zone.
# time shift in seconds
shift = UTC_OFFSET*60*60

shift_data = utc_data.copy()
shift_data.iloc[:,1:] += shift


dst_start_ind, dst_end_ind = dates.searchsorted([DST_START_DATE,DST_END_DATE])

dst_data = shift_data.copy()
dst_data.iloc[ dst_start_ind : dst_end_ind , 1: ] += 60*60


# -----------------------------------------
# ------------ MAKE PLOTS -----------------
# -----------------------------------------

newdir = '%s%d_plots' %(LOC,YEAR)

if not newdir in os.listdir():
    print('New directory: %s'%newdir)
    os.mkdir(newdir)

os.chdir(newdir)

# -----------------------------------------
# ------------ MAKE PLOTS -----------------
# -----------------------------------------

carpet_wake = time(7,0,0)
carpet_sleep = time(23,0,0)
make_sunshine_carpet_plot( carpet_wake, carpet_sleep, LOC, LOCNAME, YEAR, DPI, sunshine_carpet_colors, utc_data, UTC_OFFSET, DST_START_DATE, DST_END_DATE )

midnight = time(0,0,0)
make_daylight_hours_plot( midnight, midnight, LOC, LOCNAME, YEAR, DPI, daylight_hours_colors, shift_data )

wake_hrs = np.arange(5,12)
sleep_hrs = (wake_hrs+16)%24

work_hrs = (wake_hrs+9)%24
home_hrs = (wake_hrs+15)%24

morning_table = []
work_table = []
wake_table = []

for iii in range(len(wake_hrs)):

    wake_time = time(wake_hrs[iii],0,0)
    sleep_time = time(sleep_hrs[iii],0,0)

    work_time = time(work_hrs[iii],0,0)
    home_time = time(home_hrs[iii],0,0)

    
    wake_stats = make_daylight_hours_comparison_plot( wake_time, sleep_time, LOC, LOCNAME, YEAR, DPI, daylight_hours_colors, utc_data, shift_data, dst_data )
    wake_table.append(wake_stats)

    work_stats = make_daylight_hours_comparison_plot( work_time, home_time, LOC, LOCNAME, YEAR, DPI, daylight_hours_colors, utc_data, shift_data, dst_data )
    work_table.append(work_stats)

    morning_stats = make_sunny_morning_plot( wake_time, LOC, LOCNAME, YEAR, DPI, sunny_mornings_colors, utc_data, shift_data, dst_data )
    morning_table.append( morning_stats )

    plt.clf()
    plt.close()

os.chdir('..')



# -----------------------------------------
# ----------- PRINT TABLES ----------------
# -----------------------------------------

def print_table( table, hrs1, hrs2=None ):
    table = np.array(table).T
    table[1] -= table[0]
    table[2] -= table[0]
    table.round().astype(int)

    str0 = 'kl., '
    if hrs2 is None:
        str0 += ', '.join(['%02d'%hr for hr in hrs1])
    else:
        str0 += ', '.join(['%02d-%02d'%(hrs1[i],hrs2[i]) for i in range(len(hrs1))])

    print(str0)
    
    str1 = 'UTC, '
    str1 += ', '.join(['%d'%val for val in table[0]])
    print(str1)

    timezone = 'UTC%+d' % UTC_OFFSET
    str2 = timezone + ', '
    str2 += ', '.join(['%+d'%val for val in table[1]])
    print(str2)

    str3 = timezone + r' + sumartími, '
    str3 += ', '.join(['%+d'%val for val in table[2]])
    print(str3)
    



print('\nSunny mornings:')
print_table(morning_table, wake_hrs)

print('\nBright waking hours:')
print_table(wake_table, wake_hrs, sleep_hrs)

print('\nDaylight after work:')
print_table(work_table, work_hrs, home_hrs)







