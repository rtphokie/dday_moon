#!/usr/bin/env python

import unittest
from skyfield import api, almanac
from datetime import timedelta
from skyfield.nutationlib import iau2000b

e = api.load('de430t.bsp')  # covers 1550 Jan 01 to 2650 Jan 22, was selected for its lunar ephemeris accuracy

# globals
moon = e['moon']
earth = e['earth']
ts = api.load.timescale()
normandy = api.Topos('49.3697 N', '0.8711 W')

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
    t, y = almanac.find_discrete(t0, t1, sunrise_sunset(e, normandy, sunrise_degree_def=sunrise_degree_def))
    sunset = t[0]
    sunrise = t[1]
    return t

def get_moon_position(t, location):
    # apparent = location.at(t).observe(moon).apparent()

    boston = earth + location
    astro = boston.at(t).observe(moon)
    app = astro.apparent()

    alt, az, distance = app.altaz()
    return alt

def main():
    ''' using the sun center half a degree below the horizon to define'''
    sunset, sunrise = get_dday_sunset_sunrise(sunrise_degree_def = (-.4444))
    print ("Sunset:   %s" % sunset.utc_jpl())
    alt = get_moon_position(sunset, normandy)
    print ("Moon alt: %s" % alt.dstr())
    print ()
    print ("Sunrise: %s" % sunrise.utc_jpl())
    alt = get_moon_position(sunrise, normandy)
    print ("Moon alt: %s" % alt.dstr())

class TestDDayMoon(unittest.TestCase):
    def test_main(self):
        main()

    def test_sun_by_upperlimb_definition(self):
        # Did Dr. Olson define sunrise as when the upper limb of the Sun touches the horizon
        sunset, sunrise = get_dday_sunset_sunrise(sunrise_degree_def = (-0.5))
        sunset_olson = ts.utc(1944, 6, 5, 20, 1)
        julian_delta = sunset - sunset_olson
        delta_seconds = julian_delta * 24 * 60 * 60
        # within 30 seconds?  (rounding error to nearest minute?)
        self.assertAlmostEqual(delta_seconds, 30, 0)

    def test_sun_by_USNO_definition(self):
        sunset, sunrise = get_dday_sunset_sunrise()
        sunset_olson = ts.utc(1944, 6, 5, 20, 1)
        julian_delta = sunset - sunset_olson
        delta_minutes = julian_delta * 24 * 60
        self.assertAlmostEqual(delta_minutes, 3, 0)

    def test_moon_at_sunset(self):
        sunset, sunrise = get_dday_sunset_sunrise()
        alt = get_moon_position(sunset, normandy)
        self.assertTrue(alt.signed_dms()[0] > 0.0, 'Expected Moon to be above horizon at sunset')

    def test_moon_at_sunrise(self):
        sunset, sunrise = get_dday_sunset_sunrise()
        alt = get_moon_position(sunset, normandy)
        self.assertTrue(alt.signed_dms()[0] > 0.0, 'Expected Moon to be above horizon at sunset')

if __name__ == '__main__':
    main()
