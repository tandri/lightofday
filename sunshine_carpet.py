
import sys

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import colors  
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
NIGHT_COLOR = '#033e70'

NOON_COLOR = '#ffd923'
SLEEP_COLOR = '#1ea050'

PLOT_COLORS = [DAY_COLOR, TWI_COLOR, NIGHT_COLOR, NOON_COLOR, SLEEP_COLOR]

# -----------------------------------------
# -----------------------------------------
# -----------------------------------------

def sunshine_carpet_plot_config( ax, is_leap_year=False ):

    show_hours = np.arange(13)*2
    ylabels = [ '%02d'%(hr%24) for hr in show_hours ]
    ax.set_yticks( show_hours*60 )
    ax.set_yticklabels( ylabels )

    month_start_day = np.array([ 1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335 ])
    month_start_day[2:] += int(is_leap_year)
    xtickloc = month_start_day - 1
    # xticks = [r'Jan', r'Feb', r'Mar', r'Apr', r'Maí', r'Jún', r'Júl', r'Ágú', r'Sep', r'Okt', r'Nóv', r'Des']
    month_names = [r'jan', r'feb', r'mar', r'apr', r'maí', r'jún', r'júl', r'ágú', r'sep', r'okt', r'nóv', r'des']


    # ax.set_xticks(xtickloc)
    # ax.set_xticklabels(xticks)

    ax.xaxis.set_major_locator( ticker.FixedLocator(xtickloc) )
    ax.xaxis.set_major_formatter( ticker.NullFormatter() )

    ax.xaxis.set_minor_locator( ticker.FixedLocator(xtickloc+14) )
    ax.xaxis.set_minor_formatter( ticker.FixedFormatter( month_names ) )


    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')





def weave_carpet( data ):
    
    night_code = 0
    twi_code = 1
    day_code = 2

    # Resolution in minutes
    minutes_in_day = 60*24
    days_in_year = data.shape[0]

    thread = night_code*np.ones( days_in_year * minutes_in_day )

    twi_begin = (data[ 'twilight_begin' ]/60).round().astype(int)
    sunrise = (data[ 'sunrise' ]/60).round().astype(int)
    sunset = (data[ 'sunset' ]/60).round().astype(int)
    twi_end = (data[ 'twilight_end' ]/60).round().astype(int)

    # Paint twilight
    for day in range(days_in_year)[::-1]:
        t0 = day*minutes_in_day

        tl2 = twi_end[day]
        if tl2 < - minutes_in_day:
            # last t1
            t2 = t1
        else:
            t2 = t0 + tl2

        tl1 = twi_begin[day]
        if tl1 < - minutes_in_day:
            # next t2
            if day > 0:
                tl2 = twi_end[day-1]
            else:
                tl2 = 0
            if tl2 < - minutes_in_day:
                t1 = t0 - minutes_in_day
            else:
                t1 = t0 - minutes_in_day + tl2
        else:
            t1 = t0 + tl1

        thread[t1:t2] = twi_code

    # Paint sunlight
    for day in range(days_in_year)[::-1]:
        t0 = day*minutes_in_day

        sl2 = sunset[day]
        if sl2 < - minutes_in_day:
            t2 = t1
        else:
            t2 = t0 + sl2

        sl1 = sunrise[day]
        if sl1 < - minutes_in_day:
            # next t2
            if day > 0:
                sl2 = sunset[day-1]
            else:
                sl2 = 0
            if sl2 < - minutes_in_day:
                t1 = t0 - minutes_in_day
            else:
                t1 = t0 - minutes_in_day + sl2
        else:
            t1 = t0 + sl1

        thread[t1:t2] = day_code

    carpet = thread.reshape(( days_in_year, minutes_in_day )).T
    return carpet



def make_sunshine_carpet_plot( wake_time, sleep_time, loc_short, location_name, year, fig_dpi, plot_colors, utc_data, utc_offset, dst_start_date, dst_end_date ):

    utcCarpet = weave_carpet( utc_data )

    shift = utc_offset * 60

    thread = np.roll( utcCarpet.ravel( order='F' ), shift )
    shiftCarpet = thread.reshape( utcCarpet.shape, order='F' ).copy()


    dates = utc_data['date']
    dst_start_ind, dst_end_ind = dates.searchsorted([dst_start_date,dst_end_date])

    ind1 = dst_start_ind * 60*24
    ind2 = dst_end_ind * 60*24

    thread[ind1:ind2] = thread[ ind1-60 : ind2-60 ]
    dstCarpet = thread.reshape( utcCarpet.shape, order='F' )


    # -----------------------------------------
    # -------------- PLOT ---------------------
    # -----------------------------------------


    # night_color = '#033e70'
    # twi_color = '#106ebc'
    # day_color = '#c6e5ff'

    night_color = plot_colors[2]
    twi_color = plot_colors[1]
    day_color = plot_colors[0]


    carpet_cmap = colors.ListedColormap([night_color, twi_color, day_color])
    # carpet_cmap = 'Blues_r'
    
    # noon_color = '#ffd923'
    # sleep_color = '#1ea050'
    noon_color = plot_colors[3]
    sleep_color = plot_colors[4]
    sleep_style = '--'
    wake_minutes = wake_time.hour*60 + wake_time.minute
    sleep_minutes = sleep_time.hour*60 + sleep_time.minute


    # UTC

    fig = plt.figure(figsize=(9,4))

    ax = fig.add_subplot(1,1,1)
    ax.imshow( utcCarpet, cmap=carpet_cmap, origin='lower', interpolation='none', aspect='auto' )


    ax.plot( utc_data['noon']/60, noon_color )

    number_of_days = len(dates)
    ax.plot( [0,number_of_days-1], wake_minutes*np.ones(2), color=sleep_color, linestyle=sleep_style )
    ax.plot( [0,number_of_days-1], sleep_minutes*np.ones(2), color=sleep_color, linestyle=sleep_style )

    sunshine_carpet_plot_config( ax, is_leap_year=(number_of_days==366) )

    str1 = r'Dagsbirta' + location_name
    str2 = r' m.v. UTC'

    ax.set_title(str1+str2)

    plt.savefig('%s%d-carpet-utc.png'%(loc_short,year),dpi=fig_dpi,bbox_inches='tight')
    # plt.show()

    # -----------------------------------------
    # SHIFT

    fig = plt.figure(figsize=(9,4))

    ax = fig.add_subplot(1,1,1)
    ax.imshow( shiftCarpet, cmap=carpet_cmap, origin='lower', interpolation='none', aspect='auto' )


    ax.plot( shift+utc_data['noon']/60, noon_color )

    ax.plot( [0,number_of_days-1], wake_minutes*np.ones(2), color=sleep_color, linestyle=sleep_style )
    ax.plot( [0,number_of_days-1], sleep_minutes*np.ones(2), color=sleep_color, linestyle=sleep_style )

    sunshine_carpet_plot_config( ax, is_leap_year=(number_of_days==366) )



    str3 = '%+d' % utc_offset
    ax.set_title(str1+str2+str3)


    plt.savefig('%s%d-carpet-shift.png'%(loc_short,year),dpi=fig_dpi,bbox_inches='tight')
    # plt.show()

    # -----------------------------------------
    # DST

    fig = plt.figure(figsize=(9,4))

    ax = fig.add_subplot(1,1,1)
    ax.imshow( dstCarpet, cmap=carpet_cmap, origin='lower', interpolation='none', aspect='auto' )

    ax.plot( 60 + shift + utc_data['noon'][dst_start_ind:dst_end_ind]/60, noon_color )
    ax.plot( shift + utc_data['noon'][:dst_start_ind]/60, noon_color )
    ax.plot( shift + utc_data['noon'][dst_end_ind:]/60, noon_color )

    ax.plot( [0,number_of_days-1], wake_minutes*np.ones(2), color=sleep_color, linestyle=sleep_style )
    ax.plot( [0,number_of_days-1], sleep_minutes*np.ones(2), color=sleep_color, linestyle=sleep_style )

    sunshine_carpet_plot_config( ax, is_leap_year=(number_of_days==366) )


    str4 = r' með sumartíma'
    ax.set_title(str1+str2+str3+str4)

    plt.savefig('%s%d-carpet-dst.png'%(loc_short,year),dpi=fig_dpi,bbox_inches='tight')
    # plt.show()


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


    # -----------------------------------------
    # ------------- MAKE PLOT -----------------
    # -----------------------------------------

    make_sunshine_carpet_plot( WAKE_TIME, SLEEP_TIME, LOC, LOCNAME, YEAR, DPI, PLOT_COLORS, utc_data, UTC_OFFSET, DST_START_DATE, DST_END_DATE )

    plt.clf()
    plt.close()

