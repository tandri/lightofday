# lightofday


Compare the daylight gained and lost by using the time zone UTC or local time with or without daylight savings.
Intended for the northern hemisphere.
Does not work for extreme latitudes (>67˚N).
Not tested for longitudes far from 0˚.

Blog post (in Icelandic): https://tandrigauksson.wordpress.com/2018/01/07/ef-vid-stillum-klukkuna/

Written in: Python 3.6.2

Libraries used: sys, os, pandas, matplotlib, numpy, datetime, urllib, json


# Download data
## get_data.py

Downloads sunrise/sunset data from https://sunrise-sunset.org/ for the year YEAR at latitude LAT and longitude LNG
and saves in the file '[PLACE_NAME][YEAR].pkl'.

Usage:
python3 get_data.py

Configure the parameters YEAR, PLACE_NAME, LAT, LNG appropriately.



# Plot data
## plot_all.py

Reads data from '[LOC][YEAR].pkl', draws a variety of plots (using hours_of_daylight.py, sunny_mornings.py, sunshine_carpet.py) and saves them in './[LOC][YEAR]_plots/'.

Usage:
python3 plot_all.py

Configure the parameters YEAR, LOC, LOCNAME, UTC_OFFSET appropriately.

## hours_of_daylight.py

Using the data from '[LOC][YEAR].pkl'
draws a barplot for the average number of daylight hours of each month between h1:m1 and h2:m2
(h1,h2 in 0,1,...23, and m1,m2 in 0,1,...,59)
in UTC, local time and local time + DST.

Usage:

python3 hours_of_daylight.py

(h1=7, m1=0, h2=23, m2=0)
or

python3 hours_of_daylight.py h1 h2

(m1=m2=0)
or

python3 hours_of_daylight.py h1 m1 h2 m2

Configure the parameters YEAR, LOC, LOCNAME, UTC_OFFSET appropriately.


## sunny_mornings.py

Using the data from '[LOC][YEAR].pkl'
draws a barplot for the average number of days where it is bright at time h:m
(h in 0,1,...23, and m in 0,1,...,59)
in UTC, local time and local time + DST.

Usage:

python3 sunny_mornings.py

(h=7, m=0)
or

python3 sunny_mornings.py h

(m=0)
or

python3 sunny_mornings.py h m

Configure the parameters YEAR, LOC, LOCNAME, UTC_OFFSET appropriately.

## sunshine_carpet.py

Using the data from '[LOC][YEAR].pkl' draws a sun graph with respect to UTC, local time and local time + DST.
Dashed lines are drawn at times h1:m1 and h2:m2 (h1,h2 in 0,1,...23, and m1,m2 in 0,1,...,59).
Set h1=h2=m1=m2=0 for no such lines.

Usage:

python3 sunshine_carpet.py

(h1=7, m1=0, h2=23, m2=0)
or

python3 sunshine_carpet.py h1 h2

(m1=m2=0)
or

python3 sunshine_carpet.py h1 m1 h2 m2

Configure the parameters YEAR, LOC, LOCNAME, UTC_OFFSET appropriately.
