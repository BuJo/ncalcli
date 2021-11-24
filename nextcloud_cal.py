#!/usr/bin/env python3
"""
Python based command line extension to display Owncloud/Nextcloud calendar agenda.

Sven Schirmer, 2016, schirmer@green-orca.com
"""

import os
import sys
import configparser
import re
from dataclasses import dataclass
from datetime import datetime, date, timedelta, timezone
from dateutil.parser import isoparse

import caldav
from icalendar import Calendar


@dataclass(order=True, frozen=True)
class Event:
    """ Calendar Event """
    start: datetime
    end: datetime
    summary: str
    calendar: str


def parse_info(data, name):
    """ Parse event data into dictionary """

    cal = Calendar.from_ical(data)

    for ev in cal.subcomponents:
        estart = ev.decoded('DTSTART')
        eend = ev.decoded('DTEND')
        esummary = ev.decoded('SUMMARY').decode('UTF-8')
        if estart.__class__ != datetime:
            continue
        yield Event(calendar=name, start=estart, end=eend, summary=esummary)


if __name__ == '__main__':
    LOCAL_TIMEZONE = datetime.now(timezone(timedelta(0))).astimezone().tzinfo
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/') + '.config/nextcloud_cal.ini')

    if len(sys.argv) > 1:
        today = isoparse(sys.argv[1])
        tdelta = timedelta(days=1)
    else:
        today = date.today()
        tdelta = timedelta(days=int(config['DEFAULT']['time_delta']))

    cal_filter = '|'.join(config['DEFAULT']['cals'].split(','))
    # create client
    client = caldav.DAVClient(config['DEFAULT']['url'],
                              proxy=None, username=config['DEFAULT']['user'],
                              password=config['DEFAULT']['pwd'], auth=None,
                              ssl_verify_cert=bool(config['DEFAULT']['ssl'] == 'True'))
    # create connection
    principal = client.principal()
    calendars = principal.calendars()
    event_data = []
    # cycle through all calendars
    for calendar in calendars:
        if re.match(rf'.*/({cal_filter})/$', calendar.canonical_url) is None:
            continue
        props = calendar.get_properties([caldav.elements.dav.DisplayName(), ])
        display_name = props[caldav.elements.dav.DisplayName().tag]
        results = calendar.date_search(today, today + tdelta)
        for result_entry in results:
            for event in parse_info(result_entry.data, display_name):
                event_data.append(event)

    event_data.sort()

    currentDate = date.today() - timedelta(days=1)
    i = 0

    # output
    for result_entry in event_data:
        if i >= int(config['DEFAULT']['lines_to_display']):
            break
        datestr = result_entry.start.date().strftime('%a %d.%m')
        # avoid duplicate date output
        if result_entry.start.date() == currentDate:
            datestr = "         "
        else:
            currentDate = result_entry.start.date()
            # replace todays date with "Today"
        if result_entry.start.date() == date.today():
            datestr = "Today    "
        timestr = (result_entry.start.astimezone(LOCAL_TIMEZONE)).strftime("%H:%M")
        # all-day events
        if timestr == '00:00':
            timestr = '-all-'
        if result_entry.end:
            durationstr = "%.2f" % ((result_entry.end - result_entry.start).seconds / 60.0 / 60)
        else:
            durationstr = ''

        # output
        summary = result_entry.summary[:int(config['DEFAULT']['summary_length'])]
        sys.stdout.write(datestr + '\t' + timestr + '\t' + durationstr + '\t' + summary + os.linesep)
        i = i + 1
