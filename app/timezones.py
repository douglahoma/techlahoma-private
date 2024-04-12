#!/usr/bin/python3

import time as _time

from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)
HOUR = timedelta(hours=1)
SECOND = timedelta(seconds=1)

STDOFFSET = timedelta(seconds = -_time.timezone)

if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class USTimeZone(tzinfo):
    """According to the Python standard library, tzinfo if implemented only as
    something called an Abstract Base Class -- which is essentially a skeleton
    you use to build your own version.--"""

    #Here for compatibility reasons with more robust original
    DSTSTART_2007 = datetime(1, 3, 8, 2)
    DSTEND_2007 = datetime(1, 11, 1, 2)
    DSTSTART_1987_2006 = datetime(1, 4, 1, 2)
    DSTEND_1987_2006 = datetime(1, 10, 25, 2)
    DSTSTART_1967_1986 = datetime(1, 4, 24, 2)
    DSTEND_1967_1986 = DSTEND_1987_2006

    def __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self
        start, end = self.dst_range(dt.year)
        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        dt = dt.replace(tzinfo=None)
        if start + HOUR <= dt < end - HOUR:
            # DST is in effect.
            return HOUR
        if end - HOUR <= dt < end:
            # Fold (an ambiguous hour): use dt.fold to disambiguate.
            return ZERO if dt.fold else HOUR
        if start <= dt < start + HOUR:
            # Gap (a non-existent hour): reverse the fold rule.
            return HOUR if dt.fold else ZERO
        # DST is off.
        return ZERO

    def fromutc(self, dt):
        assert dt.tzinfo is self
        start, end = self.dst_range(dt.year)
        start = start.replace(tzinfo=self)
        end = end.replace(tzinfo=self)
        std_time = dt + self.stdoffset
        dst_time = std_time + HOUR
        if end <= dst_time < end + HOUR:
            # Repeated hour
            return std_time.replace(fold=1)
        if std_time < start or dst_time >= end:
            # Standard time
            return std_time
        if start <= std_time < end - HOUR:
            # Daylight saving time
            return dst_time

    def tznow(self):
        """The function which I had to stitch together a whole module for!!
        """
        return datetime.now(tz=self)

    @staticmethod
    def first_sunday_on_or_after(dt):
        days_to_go = 6 - dt.weekday()
        if days_to_go:
            dt += timedelta(days_to_go)
        return dt

    @classmethod
    def dst_range(cls, year):
        """Find start and end times for US DST. For years before 1967, return
        start = end for no DST."""
        if 2006 < year:
            dststart, dstend = cls.DSTSTART_2007, cls.DSTEND_2007
        elif 1986 < year < 2007:
            dststart, dstend = cls.DSTSTART_1987_2006, cls.DSTEND_1987_2006
        elif 1966 < year < 1987:
            dststart, dstend = cls.DSTSTART_1967_1986, cls.DSTEND_1967_1986
        else:
            return (datetime(year, 1, 1), ) * 2

        start = cls.first_sunday_on_or_after(dststart.replace(year=year))
        end = cls.first_sunday_on_or_after(dstend.replace(year=year))

        return (start, end)
    
Eastern  = USTimeZone(-5, "Eastern",  "EST", "EDT")
Central  = USTimeZone(-6, "Central",  "CST", "CDT")
Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific  = USTimeZone(-8, "Pacific",  "PST", "PDT")
