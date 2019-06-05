import unittest
from dday_moon import main, get_dday_sunset_sunrise, get_moon_position
from dday_moon import normandy, ts

sunset_degrees_USNO = -0.8333
sunset_degrees_simplified = -1.1

class TestDDayMoon(unittest.TestCase):
    def test_main(self):
        main()

    def test_sunset_by_upperlimb_definition(self):
        sunset_olson = ts.utc(1944, 6, 5, 20, 1) #UTC
        # Did Dr. Olson define sunrise as when the upper limb of the Sun touches the horizon
        sunset, sunrise = get_dday_sunset_sunrise(sunrise_degree_def = sunset_degrees_simplified)

        julian_delta = sunset - sunset_olson
        delta_seconds = julian_delta * 24 * 60 * 60
        # within rounding error
        self.assertTrue(abs(delta_seconds) < 30)

    def test_sunrise_by_upperlimb_definition(self):
        sunrise_olson = ts.utc(1944, 6, 6, 3, 57) #UTC
        # Did Dr. Olson define sunrise as when the upper limb of the Sun touches the horizon
        sunset, sunrise = get_dday_sunset_sunrise(sunrise_degree_def = sunset_degrees_simplified)

        julian_delta = sunrise - sunrise_olson
        delta_seconds = julian_delta * 24 * 60 * 60
        # within rounding error
        self.assertTrue(abs(delta_seconds) < 30)

    def test_sunrise_by_USNO_definition(self):
        sunrise_olson = ts.utc(1944, 6, 6, 3, 57) #UTC
        sunset, sunrise = get_dday_sunset_sunrise(sunrise_degree_def=sunset_degrees_USNO)

        julian_delta = sunrise - sunrise_olson
        delta_seconds = julian_delta * 24 * 60 * 60
        # within rounding error
        self.assertTrue(abs(delta_seconds) < 30)

    def test_sunset_by_USNO_definition(self):
        sunset_olson = ts.utc(1944, 6, 5, 20, 1)
        sunset, sunrise = get_dday_sunset_sunrise(sunrise_degree_def=sunset_degrees_USNO)

        julian_delta = sunset - sunset_olson
        delta_seconds = julian_delta * 24 * 60 * 60
        # within rounding error
        self.assertTrue(abs(delta_seconds) < 30)

    def test_moon_at_sunset(self):
        sunset, sunrise = get_dday_sunset_sunrise()
        alt = get_moon_position(sunset, normandy)
        self.assertTrue(alt.signed_dms()[0] > 0.0, 'Expected Moon to be above horizon at sunset')
