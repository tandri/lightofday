
import sys

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from datetime import date, time, timedelta


# -----------------------------------------
# ----------- CONFIG ----------------------
# -----------------------------------------

WAKE_TIME = time(7,0,0)
SLEEP_TIME = time(23,0,0)

LOC = 'RVK'
LOCNAME = r' í Reykjavík'

# LOC = 'PDL'
# LOCNAME = r' í Ponta Delgada'
YEAR = 2018
DATA_PATH = '%s%d.pkl' %(LOC,YEAR)

# Offset in hours from UTC in winter.
UTC_OFFSET = -1



# In 2018, DST starts on March 25 and ends October 28
DST_START_DATE = date(YEAR,3,25)
DST_END_DATE = date(YEAR,10,28)

plt.rc('font', family='Times New Roman')
DPI = 150

DAY_COLOR = '#c6e5ff'
TWI_COLOR = '#106ebc'

PLOT_COLORS = [DAY_COLOR, TWI_COLOR]

# -----------------------------------------
# -----------------------------------------
# -----------------------------------------

def hours_daylight_hours_plot_config( ax, hour_limit = 24 ):
    if hour_limit <= 0:
        hour_limit = 24

    # month_names = [r'Jan', r'Feb', r'Mar', r'Apr', r'Maí', r'Jún', r'Júl', r'Ágú', r'Sep', r'Okt', r'Nóv', r'Des']
    month_names = [r'jan', r'feb', r'mar', r'apr', r'maí', r'jún', r'júl', r'ágú', r'sep', r'okt', r'nóv', r'des']
    
    ax.set_xticks(range(12))
    ax.set_xticklabels(month_names)
    n_ticks = 8
    ax.set_yticks( np.arange(n_ticks+1) * np.ceil(hour_limit/n_ticks) )
    ax.set_ylim(0,hour_limit*1.05)

    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    ax.tick_params('y',right=True)


def compare_daylight_hours_plot_config( ax, hour_limit = 24 ):
    if hour_limit <= 0:
        hour_limit = 24

    # month_names = [r'Jan', r'Feb', r'Mar', r'Apr', r'Maí', r'Jún', r'Júl', r'Ágú', r'Sep', r'Okt', r'Nóv', r'Des']
    month_names = [r'jan', r'feb', r'mar', r'apr', r'maí', r'jún', r'júl', r'ágú', r'sep', r'okt', r'nóv', r'des']
    
    ax.set_xticks(range(12))
    ax.set_xticklabels(month_names)
    n_ticks = 8
    ax.set_yticks( np.arange(n_ticks+1) * np.ceil(hour_limit/n_ticks) )
    ax.set_ylim(0,hour_limit*1.05)

    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    ax.tick_params('y',right=True)





def average_daylight_by_month( data, start_time=0, stop_time=24*60*60 ):
    # 0 <= start_time, sleep_time in seconds from midnight

    dates = data['date']
    seconds_in_day = 24*60*60

    # Seperately treat the hours before and after midnight
    if stop_time > seconds_in_day:

        sunlight_hours, twilight_hours = average_daylight_by_month(data, start_time, seconds_in_day)

        residual_time = stop_time - seconds_in_day

        shifted_data = data.copy()
        shifted_data['date'] = dates - timedelta(1)

        res_sun, res_twi = average_daylight_by_month( shifted_data, 0, residual_time )

        sunlight_hours += res_sun
        twilight_hours += res_twi

        return sunlight_hours, twilight_hours

    sunrise = data['sunrise']
    sunset = data['sunset'].copy()

    twibegin = data['twilight_begin']
    twiend = data['twilight_end'].copy()

    # Very negative values indicate that the twilight does not end
    twiend[ twiend<-seconds_in_day ] = stop_time

    # Very negative values indicate that the sun does not set
    sunset[ sunset<-seconds_in_day ] = np.inf

    # # If yesterday's sun has not set
    # last_sunset = np.roll( sunset, 1 ) - seconds_in_day
    # last_twiend = np.roll( twiend, 1 ) - seconds_in_day

    # Rolling seems to be unnecessary
    last_sunset = sunset - seconds_in_day
    last_twiend = twiend - seconds_in_day

    sunrise = sunrise.clip( start_time, stop_time )
    sunset = sunset.clip( start_time, stop_time )

    last_sunset = last_sunset.clip( start_time, sunrise )
    # last_sunset = last_sunset.clip( start_time, stop_time )
    last_twiend = last_twiend.clip( last_sunset, stop_time )

    twibegin = twibegin.clip( last_twiend, stop_time )

    twiend = twiend.clip( start_time, stop_time )

    # # To see if time series are correct
    # plt.clf()
    # plt.close()
    # plt.plot(last_sunset)
    # plt.plot(last_twiend)
    # plt.plot(twibegin)
    # plt.plot(sunrise)
    # plt.plot(sunset)
    # plt.plot(twiend)
    # plt.show()

    sunlight_0 = last_sunset - start_time
    twilight_0 = last_twiend - last_sunset
    twilight_1 = sunrise - twibegin
    sunlight_1 = sunset - sunrise
    twilight_2 = twiend - sunset

    twilight = twilight_0 + twilight_1 + twilight_2
    sunlight = sunlight_0 + sunlight_1


    # Take the year of a day in the middle in case
    # the border days are from the adjacent years.
    middle_ind = len(dates) // 2
    year = dates[middle_ind].year


    first_day_of_months = [date(year,month,1) for month in range(1,13)]
    month_indices = dates.searchsorted(first_day_of_months)
    month_indices = np.append(month_indices, None) # convenience
    

    sunlight_hours = np.zeros(12)
    twilight_hours = np.zeros(12)

    for month in range(12):
        month_start = month_indices[month]
        month_end = month_indices[month+1]

        # Average sunlight, converted to hours
        sunlight_hours[month] = sunlight.iloc[month_start:month_end].mean()/3600
        # Average twilight, converted to hours
        twilight_hours[month] = twilight.iloc[month_start:month_end].mean()/3600


    return sunlight_hours, twilight_hours


def make_daylight_hours_plot( wake_time, sleep_time, loc_short, location_name, year, fig_dpi, plot_colors, data_table ):
    # -----------------------------------------
    # -------------- COUNT HOURS --------------
    # -----------------------------------------


    wake_seconds = wake_time.second+60*wake_time.minute+3600*wake_time.hour
    sleep_seconds = sleep_time.second+60*sleep_time.minute+3600*sleep_time.hour
    if sleep_seconds <= wake_seconds:
        # Going to sleep after midnight
        sleep_seconds += 24*60*60


    Daylight, Twilight = average_daylight_by_month( data_table, wake_seconds, sleep_seconds )


    # -----------------------------------------
    # -------------- PLOT ---------------------
    # -----------------------------------------


    barwidth = 0.75
    # twi_barcolor = '#106ebc'
    # day_barcolor = '#c6e5ff'

    twi_barcolor = plot_colors[1]
    day_barcolor = plot_colors[0]


    baredge = '#ffffff'


    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)

    ax.bar( range(12),
            Daylight,
            width=barwidth,
            color=day_barcolor,
            edgecolor=baredge)
    ax.bar( range(12),
            Twilight,
            bottom=Daylight,
            width=barwidth,
            color=twi_barcolor,
            edgecolor=baredge)

    awake_hours = (sleep_seconds - wake_seconds)/3600
    hours_daylight_hours_plot_config(ax, awake_hours)

    t1 = wake_time.strftime('%H:%M')
    t2 = sleep_time.strftime('%H:%M')
    str1 = r'Meðalfjöldi birtustunda' + location_name
    # str2 = r' milli kl. ' + t1+' og '+t2
    str2 = ''

    ax.set_title(str1+str2)

    ax.set_ylabel('klst.')

    plt.savefig('%s%d-daylight.png'%(loc_short,year),dpi=fig_dpi,bbox_inches='tight')
    # plt.show()



def make_daylight_hours_comparison_plot( wake_time, sleep_time, loc_short, location_name, year, fig_dpi, plot_colors, utc_data, shift_data, dst_data ):
    # -----------------------------------------
    # -------------- COUNT HOURS --------------
    # -----------------------------------------

    number_of_days = len(utc_data)
    is_leap_year = (number_of_days == 366)

    wake_seconds = wake_time.second+60*wake_time.minute+3600*wake_time.hour
    sleep_seconds = sleep_time.second+60*sleep_time.minute+3600*sleep_time.hour
    if sleep_seconds <= wake_seconds:
        # Going to sleep after midnight
        sleep_seconds += 24*60*60


    utcDaylight, utcTwilight = average_daylight_by_month( utc_data, wake_seconds, sleep_seconds )
    shiftDaylight, shiftTwilight = average_daylight_by_month( shift_data, wake_seconds, sleep_seconds )
    dstDaylight, dstTwilight = average_daylight_by_month( dst_data, wake_seconds, sleep_seconds )

    # -----------------------------------------
    # ------------- PRINT TABLE ---------------
    # -----------------------------------------

    month_days = [31,28+is_leap_year,31,30,31,30,31,31,30,31,30,31]
    month_days = np.array(month_days)

    utcTotalDaylight = (utcDaylight*month_days).sum()
    utcTotalTwilight = (utcTwilight*month_days).sum()
    shiftTotalDaylight = (shiftDaylight*month_days).sum()
    shiftTotalTwilight = (shiftTwilight*month_days).sum()
    dstTotalDaylight = (dstDaylight*month_days).sum()
    dstTotalTwilight = (dstTwilight*month_days).sum()

    print( '%s: %s - %s' % (loc_short, wake_time.strftime('%H:%M'), sleep_time.strftime('%H:%M')) ) 
    print( '\tClock,\tSunlight,\tTwilight' )
    print( '\tUTC,\t%.2f,\t%.2f' % (utcTotalDaylight, utcTotalTwilight) )
    print( '\tLocal,\t%.2f,\t%.2f' % (shiftTotalDaylight, shiftTotalTwilight) )
    print( '\tDST,\t%.2f,\t%.2f' % (dstTotalDaylight, dstTotalTwilight) )
    
    stats = np.array([ utcTotalDaylight+utcTotalTwilight, shiftTotalDaylight+shiftTotalTwilight, dstTotalDaylight+dstTotalTwilight ])
    
    # -----------------------------------------
    # -------------- PLOT ---------------------
    # -----------------------------------------

    barwidth = 0.25
    # twi_barcolor = '#5e5bff'
    # day_barcolor = '#83c7ff'

    twi_barcolor = plot_colors[1]
    day_barcolor = plot_colors[0]
    baredge = '#ffffff'

    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)

    ax.bar( np.arange(12)-barwidth,
            utcDaylight,
            width=barwidth,
            color=day_barcolor,
            edgecolor=baredge)
    ax.bar( np.arange(12)-barwidth,
            utcTwilight,
            bottom=utcDaylight,
            width=barwidth,
            color=twi_barcolor,
            edgecolor=baredge)


    ax.bar( np.arange(12),
            shiftDaylight,
            width=barwidth,
            color=day_barcolor,
            edgecolor=baredge)
    ax.bar( np.arange(12),
            shiftTwilight,
            bottom=shiftDaylight,
            width=barwidth,
            color=twi_barcolor,
            edgecolor=baredge)



    ax.bar( np.arange(12)+barwidth,
            dstDaylight,
            width=barwidth,
            color=day_barcolor,
            edgecolor=baredge)
    ax.bar( np.arange(12)+barwidth,
            dstTwilight,
            bottom=dstDaylight,
            width=barwidth,
            color=twi_barcolor,
            edgecolor=baredge)

    awake_hours = (sleep_seconds - wake_seconds)/3600

    compare_daylight_hours_plot_config(ax, awake_hours)

    t1 = wake_time.strftime('%H:%M')
    t2 = sleep_time.strftime('%H:%M')
    str1 = r'Meðalfjöldi birtustunda' + location_name
    str2 = r' milli kl. ' + t1+' og '+t2

    ax.set_title(str1+str2)


    ax.set_ylabel('klst.')

    timestring = wake_time.strftime('%H%M') + '-' + sleep_time.strftime('%H%M')
    plt.savefig('%s%d-daylightcompare-%s.png'%(loc_short,year,timestring),dpi=fig_dpi,bbox_inches='tight')
    # plt.show()

    return stats


if __name__ == '__main__':
    
    # -----------------------------------------
    # ------------- CHECK COMMAND LINE --------
    # -----------------------------------------

    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            wake_hr = int( sys.argv[1] )
            wake_min = 0
            sleep_hr = int( sys.argv[2] )
            sleep_min = 0

        if len(sys.argv) == 5:
            wake_hr = int( sys.argv[1] )
            wake_min = int( sys.argv[2] )
            sleep_hr = int( sys.argv[3] )
            sleep_min = int( sys.argv[4] )

        WAKE_TIME = time( wake_hr, wake_min, 0 )
        SLEEP_TIME = time( sleep_hr, sleep_min, 0 )

    # -----------------------------------------
    # ------------- LOAD DATA -----------------
    # -----------------------------------------


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
    # ------------- MAKE PLOT -----------------
    # -----------------------------------------

    midnight = time(0,0,0)
    make_daylight_hours_plot( midnight, midnight, LOC, LOCNAME, YEAR, DPI, PLOT_COLORS, shift_data )
    make_daylight_hours_comparison_plot( WAKE_TIME, SLEEP_TIME, LOC, LOCNAME, YEAR, DPI, PLOT_COLORS, utc_data, shift_data, dst_data )

    plt.clf()
    plt.close()

