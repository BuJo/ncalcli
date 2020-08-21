from unittest import TestCase
from datetime import datetime, timezone

import nextcloud_cal


class Test(TestCase):
    EVENT = '''BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//Sabre//Sabre VObject 4.3.0//EN\r
CALSCALE:GREGORIAN\r
BEGIN:VEVENT\r
CREATED:20200810T145113Z\r
DTSTAMP:20200810T145115Z\r
LAST-MODIFIED:20200810T145115Z\r
SEQUENCE:0\r
UID:81a78add-1f47-4e9e-a4bb-42999747a8a2\r
DTSTART:20200821T083000Z\r
DTEND:20200821T091500Z\r
ORGANIZER;CN=scherer:mailto:test@example.com\r
SUMMARY:Daily\r
DESCRIPTION:yoohoo\r
COLOR:mediumpurple\r
RELATED-TO;RELTYPE=SIBLING:1c875e16-da34-4ecb-8297-a400f0733a04\r
RECURRENCE-ID:20200821T083000Z\r
END:VEVENT\r
END:VCALENDAR\r
'''

    def test_parse_info(self):
        info = nextcloud_cal.parse_info(Test.EVENT, 'title')
        assert info['CAL'] == 'title'
        assert info['SUMMARY'] == 'Daily'
        assert info['DSTART'] == datetime(2020, 8, 21, 8, 30, tzinfo=timezone.utc)
        assert info['DEND'] == datetime(2020, 8, 21, 9, 15, tzinfo=timezone.utc)
