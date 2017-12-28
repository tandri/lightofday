
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
BACKGROUND_COLOR = '#eaeeff'

PLOT_COLORS = [DAY_COLOR, TWI_COLOR, BACKGROUND_COLOR]
# -----------------------------------------
# -----------------------------------------
# -----------------------------------------


def sunny_morning_plot_config( ax ):
    # month_names = [r'Jan', r'Feb', r'Mar', r'Apr', r'Maí', r'Jún', r'Júl', r'Ágú', r'Sep', r'Okt', r'Nóv', r'Des']
    month_names = [r'jan', r'feb', r'mar', r'apr', r'maí', r'jún', r'júl', r'ágú', r'sep', r'okt', r'nóv', r'des']

    ax.set_xticks(range(12))
    ax.set_xticklabels(month_names)

    ax.set_yticks(np.arange(-1,11)*3)
    ax.set_ylim(0,32)

    for tick in ax.xaxis.get_major_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')


    ax.tick_params('y',right=True)
    # ax.legend(bbox_to_anchor=(1.05, 1.0), loc=2, borderaxespad=0.)






def sunny_mornings_by_month( data, wake_time ):
    # wake_time in seconds

    dates = data['date']
    year = dates[0].year

    days_in_year = len(dates)
    seconds_in_day = 24*60*60
    ind = np.arange(days_in_year)

    sun_does_not_set = ind[data['sunset'] < -seconds_in_day]
    twilight_does_not_end = ind[data['twilight_end'] < -seconds_in_day]

    is_it_already = (wake_time >= data.iloc[:,1:])

    is_it_already['sunset'].iloc[sun_does_not_set] = False
    is_it_already['twilight_end'].iloc[twilight_does_not_end] = False

    sunny = is_it_already['sunrise'] * (1-is_it_already['sunset'])

    twilight = is_it_already['twilight_begin']  \
                * (1-is_it_already['twilight_end']) \
                * (1-sunny)

    first_day_of_months = [date(year,month,1) for month in range(1,13)]
    month_indices = dates.searchsorted(first_day_of_months)
    # convenience:
    month_indices = np.append(month_indices, -1)

    sunny_mornings = np.zeros(12)
    twilight_mornings = np.zeros(12)

    for month in range(12):
        month_start = month_indices[month]
        month_end = month_indices[month+1]

        sunny_mornings[month] = sunny.iloc[month_start:month_end].sum()
        twilight_mornings[month] = twilight.iloc[month_start:month_end].sum()

    return sunny_mornings, twilight_mornings


def make_sunny_morning_plot( wake_time, loc_short, location_name, year, fig_dpi, plot_colors, utc_data, shift_data, dst_data ):
    # -----------------------------------------
    # -------------- COUNT DAYS ---------------
    # -----------------------------------------

    number_of_days = len(utc_data)
    is_leap_year = (number_of_days == 366)

    wake_seconds = wake_time.second+60*wake_time.minute+3600*wake_time.hour

    utcSunMorn, utcTwiMorn = sunny_mornings_by_month( utc_data, wake_seconds )
    shiftSunMorn, shiftTwiMorn = sunny_mornings_by_month( shift_data, wake_seconds )
    dstSunMorn, dstTwiMorn = sunny_mornings_by_month( dst_data, wake_seconds )

    # -----------------------------------------
    # ------------- PRINT TABLE ---------------
    # -----------------------------------------

    utcTotalSun = utcSunMorn.sum()
    utcTotalTwi = utcTwiMorn.sum()
    shiftTotalSun = shiftSunMorn.sum()
    shiftTotalTwi = shiftTwiMorn.sum()
    dstTotalSun = dstSunMorn.sum()
    dstTotalTwi = dstTwiMorn.sum()

    print( '%s: %s' % (loc_short, wake_time.strftime('%H:%M')) )
    print( '\tClock,\tSunlight,\tTwilight' )
    print( '\tUTC,\t%d,\t\t%d' % (utcTotalSun, utcTotalTwi) )
    print( '\tLocal,\t%d,\t\t%d' % (shiftTotalSun, shiftTotalTwi) )
    print( '\tDST,\t%d,\t\t%d' % (dstTotalSun, dstTotalTwi) )

    stats = np.array([ utcTotalSun+utcTotalTwi, shiftTotalSun+shiftTotalTwi, dstTotalSun+dstTotalTwi ])

    # -----------------------------------------
    # -------------- PLOT ---------------------
    # -----------------------------------------

    barwidth = 0.25
    # barwidth = 0.375
    # background_barcolor = '#eaeeff'
    background_barcolor = plot_colors[2]

    baredge = '#ffffff'

    # twi_barcolor = '#106ebc'
    # day_barcolor = '#c6e5ff'


    twi_barcolor = plot_colors[1]
    day_barcolor = plot_colors[0]

    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)

    # background bars
    month_days = [31,28+is_leap_year,31,30,31,30,31,31,30,31,30,31]
    ax.bar( np.arange(12),
            month_days,
            width=3*barwidth,
            # width=2*barwidth,
            color=background_barcolor,
            edgecolor=baredge,
            label=r'Dagar í mánuði')


    ax.bar( np.arange(12)-barwidth,
            utcSunMorn,
            width=barwidth,
            color=day_barcolor,
            edgecolor=baredge)
    ax.bar( np.arange(12)-barwidth,
            utcTwiMorn,
            bottom=utcSunMorn,
            width=barwidth,
            color=twi_barcolor,
            edgecolor=baredge)




    ax.bar(
            np.arange(12),
            # np.arange(12)-barwidth/2,
            shiftSunMorn,
            width=barwidth,
            color=day_barcolor,
            edgecolor=baredge,
            label=r'Sólarljós')
    ax.bar(
            np.arange(12),
            # np.arange(12)-barwidth/2,
            shiftTwiMorn,
            bottom=shiftSunMorn,
            width=barwidth,
            color=twi_barcolor,
            edgecolor=baredge,
            label=r'Ljósaskipti')


    ax.bar(
            np.arange(12)+barwidth,
            # np.arange(12)+barwidth/2,
            dstSunMorn,
            width=barwidth,
            color=day_barcolor,
            edgecolor=baredge)
    ax.bar(
            np.arange(12)+barwidth,
            # np.arange(12)+barwidth/2,
            dstTwiMorn,
            bottom=dstSunMorn,
            width=barwidth,
            color=twi_barcolor,
            edgecolor=baredge)

    sunny_morning_plot_config(ax)

    # locstring = ''
    locstring = location_name
    wakestring = wake_time.strftime('%H:%M')

    ax.set_title('Dagsbirta kl. '+wakestring+locstring)

    ax.set_ylabel('dagar')

    wakestring = wake_time.strftime('%H%M')
    plt.savefig('%s%d-sunnymornings-%s.png'%(loc_short,year,wakestring),dpi=fig_dpi,bbox_inches='tight')
    # plt.show()

    return stats



if __name__ == '__main__':
    
    # -----------------------------------------
    # ------------- CHECK COMMAND LINE --------
    # -----------------------------------------

    if len(sys.argv) > 1:
        wake_hr = int( sys.argv[1] )
        if len(sys.argv) > 2:
            wake_min = int( sys.argv[2] )
        else:
            wake_min = 0
        WAKE_TIME = time( wake_hr, wake_min, 0 )

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

    make_sunny_morning_plot( WAKE_TIME, LOC, LOCNAME, YEAR, DPI, PLOT_COLORS, utc_data, shift_data, dst_data )

    plt.clf()
    plt.close()
