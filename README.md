# ncalcli

Python based command line extension to display ownCloud/Nextcloud calendar agenda.

## Requirements

- Python3.7+
- `pip3 install -r requirements.txt`

## Usage

- create `~/.config/nextcloud_cal.ini`. Use the following syntax:

```ini
[DEFAULT]
user=user
pwd=guggus
url=https://yourserver/remote.php/dav/calendars/user/default/
cals=personal
ssl=True # || False (in case your certificate can't be verified)
summary_length=20
lines_to_display=10
time_delta=20
```
