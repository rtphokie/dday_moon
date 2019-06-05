import unittest
from skyfield import api, almanac
from pytz import timezone
from skyfield.nutationlib import iau2000b
London = timezone('Europe/London')

# JPL's latest de430 (covers 1550 Jan 01 to 2650 Jan 22) was selected for its
# lunar ephemeris accuracy
e = api.load('de430t.bsp')
moon = e['moon']
earth = e['earth']

sunset_degrees_USNO = -0.8333
sunset_degrees_simplified = -1.0

# globals
ts = api.load.timescale()
normandy = api.Topos('49.25 N', '0.26667 W')

def sunrise_sunset(ephemeris, topos, sunrise_degree_def=-0.8333):

    """returns whether the sun is up. defaults to USNO definition of sunrise/set
       center of the sun 0.8333 degress below the horizon.  adapted from Skyfield's
       version of this function to allow horizon to be redefined
    """
    sun = ephemeris['sun']
    topos_at = (ephemeris['earth'] + topos).at

    def is_sun_up_at(t):
        """Return `True` if the sun has risen by time `t`."""
        t._nutation_angles = iau2000b(t.tt)
        return topos_at(t).observe(sun).apparent().altaz()[0].degrees > sunrise_degree_def

    is_sun_up_at.rough_period = 0.5  # twice a day
    return is_sun_up_at

def get_dday_sunset_sunrise(sunrise_degree_def = -0.8333):
    t0 = ts.utc(1944, 6, 5, 12)  # start looking for sunset at noon Jun 5
    t1 = ts.utc(1944, 6, 6, 12)  # stop looking for sunrise at noon Jun 6
    t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(e, normandy))
    # t, y = almanac.find_discrete(t0, t1, sunrise_sunset(e, normandy, sunrise_degree_def=sunrise_degree_def))
    return t[:2]

def get_moon_position(t, location):
    # apparent = location.at(t).observe(moon).apparent()

    boston = earth + location
    astro = boston.at(t).observe(moon)
    app = astro.apparent()

    alt, az, distance = app.altaz()
    return alt

def main():
    ''' Dr Olson appears to be using a simplified version of the USNO definition of sunrise/set
        with the center of the disk of the Sun 1.1 degrees below the horizon instead of -0.8333
        to account for the angular diameter of the Sun and atmospheric diffraction '''
    sunset, sunrise = get_dday_sunset_sunrise(sunrise_degree_def = sunset_degrees_simplified)


    print ("D-Day Sun and Moon at Normandy (%s)" % normandy)
    print ("Sunset:    %s" % str(sunset.astimezone(London)))
    print ("Moon alt:  %s\n" % get_moon_position(sunset, normandy).dstr())

    print ("Sunrise:    %s" % str(sunrise.astimezone(London)))
    print ("Moon alt: %s" % get_moon_position(sunrise, normandy).dstr())

if __name__ == '__main__':
    main()
