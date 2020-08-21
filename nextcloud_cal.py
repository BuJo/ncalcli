#!/usr/bin/env python3
"""
Python based command line extension to display Owncloud/Nextcloud calendar agenda.

Sven Schirmer, 2016, schirmer@green-orca.com
"""

import os
import sys
import configparser
import re
from datetime import datetime, date, timedelta, timezone

import caldav


def parse_info(data, name):
    """ Parse event data into dictionary """

    events = re.split("END:VEVENT\r\nBEGIN:VEVENT\r\n|END:VEVENT\r\nEND:VCALENDAR\r\n\r\n", data)
    for ev in events:
        pieces = ev.split('\r\n')
        keys = []
        values = []
        for piece in pieces:
            kv = piece.split(':')
            if kv[0] == 'SUMMARY' and kv[1] != "Alarm notification":
                keys.append(kv[0])
                values.append(kv[1])
            elif kv[0].split(';')[0] == 'DTSTART':
                keys.append('DSTART')
                values.append(parse_date(kv[1]))
            elif kv[0].split(';')[0] == 'DTEND':
                t_end = parse_date(kv[1])
                keys.append('DEND')
                values.append(t_end)
        keys.append('CAL')
        values.append(name)
        return dict(list(zip(keys, values)))


def parse_date(date_str):
    """Parse RFC 3339 Date"""

    pieces = date_str.split('T')
    if len(pieces) == 1:
        dt = datetime.strptime(date_str, "%Y%m%d")
    else:
        date_str = re.sub(r'Z$', '+00:00', date_str)
        dt = datetime.strptime(date_str, "%Y%m%dT%H%M%S%z")
    return dt


def get_dtstart(item):
    """Get start date from event"""

    return item["DSTART"]


if __name__ == '__main__':
    LOCAL_TIMEZONE = datetime.now(timezone(timedelta(0))).astimezone().tzinfo
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/') + '.config/nextcloud_cal.ini')
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
        results = calendar.date_search(date.today(),
                                       date.today() + timedelta(days=int(config['DEFAULT']['time_delta'])))
        for event in results:
            event_data.append(parse_info(event.data, display_name))

    # sort by datetime
    event_data = sorted(event_data, key=get_dtstart)

    currentDate = date.today() - timedelta(days=1)
    i = 0

    # output
    for event in event_data:
        if i >= int(config['DEFAULT']['lines_to_display']):
            break
        datestr = event['DSTART'].date().strftime('%a %d.%m')
        # avoid duplicate date output
        if event['DSTART'].date() == currentDate:
            datestr = "         "
        else:
            currentDate = event['DSTART'].date()
            # replace todays date with "Today"
        if event['DSTART'].date() == date.today():
            datestr = "Today    "
        timestr = (event['DSTART'].astimezone(LOCAL_TIMEZONE)).strftime("%H:%M")
        # all-day events
        if timestr == '00:00':
            timestr = '-all-'
        if 'DEND' in event.keys():
            durationstr = "%.2f" % ((event['DEND'] - event['DSTART']).seconds / 60.0 / 60)
        else:
            durationstr = ''

        # actual output generation with colors depending on keywords
        summary = event['SUMMARY'][:int(config['DEFAULT']['summary_length'])]
        sys.stdout.write(datestr + '  ' + timestr + '  ' + durationstr + ' ' + summary + os.linesep)
        i = i + 1
