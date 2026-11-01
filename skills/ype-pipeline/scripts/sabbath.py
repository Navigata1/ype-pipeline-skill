"""Sabbath observance: no pipeline work from Friday sunset to Saturday sunset.

The window is computed offline from the workspace settings (location and time
zone) with the NOAA sunrise equation, which is accurate to about a minute. Work
stops a configured number of minutes before Friday sunset and may resume after
Saturday sunset. A paused run keeps its state; it is not ended.
"""
from __future__ import annotations
import datetime as dt, math, time
from zoneinfo import ZoneInfo

DEFAULTS={'enabled':True,'rule':'friday-sunset-to-saturday-sunset','location':'Huntsville, AL','latitude':34.7304,'longitude':-86.5861,'timezone':'America/Chicago','stop_minutes_before_sunset':15}
EXEMPT={'status','sabbath'}
clock=time.time  # replaced in tests

def config(settings):
    cfg={**DEFAULTS,**((settings or {}).get('sabbath') or {})}
    if not -90<=float(cfg['latitude'])<=90 or not -180<=float(cfg['longitude'])<=180:raise ValueError('Sabbath location latitude/longitude out of range.')
    if not 0<=int(cfg['stop_minutes_before_sunset'])<=120:raise ValueError('stop_minutes_before_sunset must be 0..120.')
    ZoneInfo(cfg['timezone'])
    return cfg

def sunset(day,lat,lon,tz):
    """Sunset on a local calendar day, as a Unix time (NOAA sunrise equation)."""
    rad=math.radians
    for offset in (0,-1,1):
        n=(dt.date(day.year,day.month,day.day)-dt.date(2000,1,1)).days+offset
        j=n-lon/360
        m=(357.5291+0.98560028*j)%360
        c=1.9148*math.sin(rad(m))+0.02*math.sin(rad(2*m))+0.0003*math.sin(rad(3*m))
        lam=(m+c+180+102.9372)%360
        transit=2451545.0+j+0.0053*math.sin(rad(m))-0.0069*math.sin(rad(2*lam))
        dec=math.asin(math.sin(rad(lam))*math.sin(rad(23.4397)))
        cos_w=(math.sin(rad(-0.833))-math.sin(rad(lat))*math.sin(dec))/(math.cos(rad(lat))*math.cos(dec))
        if not -1<=cos_w<=1:raise ValueError('No sunset at this latitude on '+str(day)+'; set an explicit observance location.')
        value=(transit+math.degrees(math.acos(cos_w))/360-2440587.5)*86400
        if dt.datetime.fromtimestamp(value,tz).date()==day:return value
    raise ValueError('Could not place sunset on '+str(day))

def window(friday,cfg):
    tz=ZoneInfo(cfg['timezone']);lat,lon=float(cfg['latitude']),float(cfg['longitude'])
    start=sunset(friday,lat,lon,tz)-60*int(cfg['stop_minutes_before_sunset'])
    end=sunset(friday+dt.timedelta(days=1),lat,lon,tz)
    return start,end

def state(settings=None,now=None):
    """Return whether the observance window is active, and its bounds."""
    cfg=config(settings);now=clock() if now is None else float(now);tz=ZoneInfo(cfg['timezone'])
    if not cfg['enabled']:return {'active':False,'enabled':False,'note':'Observance disabled in settings.'}
    today=dt.datetime.fromtimestamp(now,tz).date()
    last_friday=today-dt.timedelta(days=(today.weekday()-4)%7)
    for friday in (last_friday,last_friday+dt.timedelta(days=7)):
        start,end=window(friday,cfg)
        if now<end:
            iso=lambda t:dt.datetime.fromtimestamp(t,tz).isoformat(timespec='minutes')
            return {'active':start<=now,'enabled':True,'starts_at':start,'ends_at':end,'starts_local':iso(start),'ends_local':iso(end),'location':cfg['location'],'rule':cfg['rule'],'stop_minutes_before_sunset':int(cfg['stop_minutes_before_sunset'])}
    raise AssertionError('unreachable: next window always ends after now')

def seconds_until_start(settings=None,now=None):
    s=state(settings,now)
    if not s.get('enabled'):return math.inf
    return 0.0 if s['active'] else s['starts_at']-(clock() if now is None else now)
