#!/usr/bin/env python
"""
Unshare or Remove users who have been inactive for X days. Prints out last seen for all users.

Just run. 

Comment out `remove_friend(username)` and `unshare(username)` to test.
"""

import requests
import datetime
import time
from plexapi.server import PlexServer, CONFIG


## EDIT THESE SETTINGS ##
TAUTULLI_URL = ''
TAUTULLI_APIKEY = ''
TAUTULLI_URL = CONFIG.data['auth'].get('tautulli_baseurl', TAUTULLI_URL)
TAUTULLI_APIKEY = CONFIG.data['auth'].get('tautulli_apikey', TAUTULLI_APIKEY)

PLEX_URL = ''
PLEX_TOKEN = ''
PLEX_URL = CONFIG.data['auth'].get('server_baseurl', PLEX_URL)
PLEX_TOKEN = CONFIG.data['auth'].get('server_token', PLEX_TOKEN)

REMOVE_LIMIT = 30 # days
UNSHARE_LIMIT = 15 # days

USER_IGNORE = ('user1')
##/EDIT THESE SETTINGS ##

sess = requests.Session()
# Ignore verifying the SSL certificate
sess.verify = False  # '/path/to/certfile'
# If verify is set to a path to a directory,
# the directory must have been processed using the c_rehash utility supplied
# with OpenSSL.
if sess.verify is False:
    # Disable the warning that the request is insecure, we know that...
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=sess)

sections_lst = [x.title for x in plex.library.sections()]
today = time.mktime(datetime.datetime.today().timetuple())


def get_users_table():
    # Get the Tautulli history.
    payload = {'apikey': TAUTULLI_APIKEY,
               'cmd': 'get_users_table',
               'order_column': 'last_seen',
               'order_dir': 'asc'}

    try:
        r = requests.get(TAUTULLI_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()

        res_data = response['response']['data']['data']
        return [data for data in res_data if data['last_seen']]

    except Exception as e:
        print("Tautulli API 'get_history' request failed: {0}.".format(e))


def unshare(user):
    print('{user} has reached inactivity limit. Unsharing.'.format(user=user))
    plex.myPlexAccount().updateFriend(user=user, server=plex, removeSections=True, sections=sections_lst)
    print('Unshared all libraries from {user}.'.format(user=user))


def remove_friend(user):
    print('{user} has reached inactivity limit. Removing.'.format(user=user))
    plex.myPlexAccount().removeFriend(user)
    print('Removed {user}.'.format(user=user))


def main():

    user_tables = get_users_table()

    for user in user_tables:
        last_seen = (today - user['last_seen']) / 24 / 60 / 60
        if int(last_seen) != 0:
            last_seen = int(last_seen)

        username = user['friendly_name']
        if username not in USER_IGNORE:
            if last_seen > REMOVE_LIMIT:
                print('{} was last seen {} days ago. Removing.'.format(username, last_seen))
                remove_friend(username)
            elif last_seen > UNSHARE_LIMIT:
                print('{} was last seen {} days ago. Unshsring.'.format(username, last_seen))
                unshare(username)
            elif last_seen > 1:
                print('{} was last seen {} days ago.'.format(username, last_seen))
            elif int(last_seen) == 1:
                print('{} was last seen yesterday.'.format(username))
            else:
                hours_ago = last_seen * 24
                if int(hours_ago) != 0:
                    hours_ago = int(hours_ago)
                    print('{} was last seen {} hours ago.'.format(username, hours_ago))
                else:
                    minutes_ago = int(hours_ago * 60)
                    print('{} was last seen {} minutes ago.'.format(username, minutes_ago))


if __name__ == '__main__':
    main()
