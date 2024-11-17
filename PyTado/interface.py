"""
PyTado interface implementation for mytado.com
"""

import logging
import json
import datetime
import urllib.request
import urllib.parse
import urllib.error

from http.cookiejar import CookieJar


_LOGGER = logging.getLogger(__name__)


class Tado:
    """Interacts with a Tado thermostat via public API.
    Example usage: t = Tado('me@somewhere.com', 'mypasswd')
                   t.getClimate(1) # Get climate, zone 1.
    """

    _debugCalls = False

    # Instance-wide constant info
    headers = {'Referer' : 'https://my.tado.com/'}
    api2url = 'https://my.tado.com/api/v2/homes/'
    mobi2url = 'https://my.tado.com/mobile/1.9/'
    hops2url = 'https://hops.tado.com/homes'
    refresh_token = ''
    refresh_at = datetime.datetime.now() + datetime.timedelta(minutes=5)

    # 'Private' methods for use in class, Tado mobile API V1.9.
    def _mobile_api_call(self, cmd):

        self._refresh_token()

        if self._debugCalls:
            _LOGGER.debug("mobile api: %s",
                          cmd)

        url = '%s%s' % (self.mobi2url, cmd)
        req = urllib.request.Request(url, headers=self.headers)
        response = self.opener.open(req)
        str_response = response.read().decode('utf-8')

        if self._debugCalls:
            _LOGGER.debug("mobile api: %s, response: %s",
                          cmd, response)

        data = json.loads(str_response)
        return data

    # 'Private' methods for use in class, Tado API V2.
    def _api_call(self, cmd, method="GET", data=None, plain=False):

        self._refresh_token()

        headers = self.headers

        if data is not None:
            if plain:
                headers['Content-Type'] = 'text/plain;charset=UTF-8'
            else:
                headers['Content-Type'] = 'application/json;charset=UTF-8'
            headers['Mime-Type'] = 'application/json;charset=UTF-8'
            data = json.dumps(data).encode('utf8')

        if self._debugCalls:
            _LOGGER.debug("api call: %s: %s, headers %s, data %s",
                          method, cmd, headers, data)

        url = '%s%i/%s' % (self.api2url, self.id, cmd)
        req = urllib.request.Request(url,
                                     headers=headers,
                                     method=method,
                                     data=data)

        response = self.opener.open(req)

        if self._debugCalls:
            _LOGGER.debug("api call: %s: %s, response %s",
                          method, cmd, response)

        str_response = response.read().decode('utf-8')
        if str_response is None or str_response == "":
            return

        data = json.loads(str_response)
        return data


    # 'Private' methods for use in class, Tado API V2.
    def _hops_api_call(self, cmd, method="GET", data=None, plain=False):

        self._refresh_token()

        headers = self.headers

        if data is not None:
            if plain:
                headers['Content-Type'] = 'text/plain;charset=UTF-8'
            else:
                headers['Content-Type'] = 'application/json;charset=UTF-8'
            headers['Mime-Type'] = 'application/json;charset=UTF-8'
            data = json.dumps(data).encode('utf8')

        if self._debugCalls:
            _LOGGER.debug("api call: %s: %s, headers %s, data %s",
                          method, cmd, headers, data)
        url = f'{self.hops2url}/{self.id}/{cmd}'
        req = urllib.request.Request(url,
                                     headers=headers,
                                     method=method,
                                     data=data)

        response = self.opener.open(req)

        if self._debugCalls:
            _LOGGER.debug("api call: %s: %s, response %s",
                          method, cmd, response)

        str_response = response.read().decode('utf-8')
        if str_response is None or str_response == "":
            return

        data = json.loads(str_response)
        return data

    def _set_o_auth_header(self, data):

        access_token = data['access_token']
        expires_in = float(data['expires_in'])
        refresh_token = data['refresh_token']

        self.refresh_token = refresh_token
        self.refresh_at = datetime.datetime.now()
        self.refresh_at = self.refresh_at + datetime.timedelta(seconds=expires_in)

        # we substract 30 seconds from the correct refresh time
        # then we have a 30 seconds timespan to get a new refresh_token
        self.refresh_at = self.refresh_at + datetime.timedelta(seconds=-30)

        self.headers['Authorization'] = 'Bearer ' + access_token

    def _refresh_token(self):
        if self.refresh_at >= datetime.datetime.now():
            return False

        url = 'https://auth.tado.com/oauth/token'
        data = {'client_id' : 'public-api-preview',
                'client_secret' : '4HJGRffVR8xb3XdEUQpjgZ1VplJi6Xgw',
                'grant_type' : 'refresh_token',
                'scope' : 'home.user',
                'refresh_token' : self.refresh_token}
        # pylint: disable=R0204
        data = urllib.parse.urlencode(data)
        url = url + '?' + data
        req = urllib.request.Request(url, data=json.dumps({}).encode('utf8'), method='POST',
                                     headers={'Content-Type': 'application/json',
                                              'Referer' : 'https://my.tado.com/'})

        response = self.opener.open(req)
        str_response = response.read().decode('utf-8')

        self._set_o_auth_header(json.loads(str_response))
        return response

    def _login_v2(self, username, password):

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        url = 'https://auth.tado.com/oauth/token'
        data = {'client_id' : 'public-api-preview',
                'client_secret' : '4HJGRffVR8xb3XdEUQpjgZ1VplJi6Xgw',
                'grant_type' : 'password',
                'password' : password,
                'scope' : 'home.user',
                'username' : username}
        # pylint: disable=R0204
        data = urllib.parse.urlencode(data)
        url = url + '?' + data
        req = urllib.request.Request(url, data=json.dumps({}).encode('utf8'), method='POST',
                                     headers={'Content-Type': 'application/json',
                                              'Referer' : 'https://my.tado.com/'})

        response = self.opener.open(req)
        str_response = response.read().decode('utf-8')

        self._set_o_auth_header(json.loads(str_response))
        return response

    def set_debugging(self, debug_calls):
        self._debugCalls = debug_calls
        return self._debugCalls

    # Public interface
    def get_me(self) -> dict:
        """Gets home information."""
        url = 'https://my.tado.com/api/v2/me'
        req = urllib.request.Request(url, headers=self.headers)
        response = self.opener.open(req)
        str_response = response.read().decode('utf-8')
        data = json.loads(str_response)
        return data

    def get_rooms_and_devices(self) -> dict:
        """Gets room and device information."""
        cmd = 'roomsAndDevices'
        data = self._hops_api_call(cmd)
        return data

    def get_rooms(self) -> list[dict]:
        """Gets rooms information."""
        cmd = 'rooms'
        data = self._hops_api_call(cmd)
        return data

    def get_room(self, room_id: int) -> dict:
        """Gets room information."""
        cmd = f'rooms/{room_id}'
        data = self._hops_api_call(cmd)
        return data

    def get_room_day_report(self, room_id: int, date: datetime.date) -> dict:
        """Gets room day report with temperature, humidity, heating and weather information."""
        cmd = f'zones/{room_id}/dayReport?date={date.strftime('%Y-%m-%d')}'
        data = self._api_call(cmd)
        return data

    def get_air_comfort(self) -> dict:
        """Gets air comfort information with current temperature, humidity and open window detection."""
        cmd = f'airComfort'
        data = self._hops_api_call(cmd)
        return data

    def get_tado_mode(self) -> dict:
        """Gets tado mode."""
        cmd = f'state'
        data = self._api_call(cmd)
        return data['presence']

    def set_home(self) -> None:
        """Sets tado mode to home."""
        cmd = f'presenceLock'
        data = self._api_call(cmd, method="PUT", data={"homePresence": "HOME"})
        return data

    def set_away(self) -> None:
        """Sets tado mode to away."""
        cmd = f'presenceLock'
        data = self._api_call(cmd, method="PUT", data={"homePresence": "AWAY"})
        return data

    def boost_heating(self) -> None:
        """Boost mode, expires after 30 minutes."""
        cmd = f'quickActions/boost'
        data = self._hops_api_call(cmd, method="POST")
        return data

    def disable_heating(self) -> None:
        """Sets all rooms off, frost protection."""
        cmd = f'quickActions/allOff'
        data = self._hops_api_call(cmd, method="POST")
        return data

    def resume_schedule(self) -> None:
        """Resumes regular schedule for all rooms, undo boost, disable heating and manual settings."""
        cmd = f'quickActions/resumeSchedule'
        data = self._hops_api_call(cmd, method="POST")
        return data

    def get_room_schedule(self, room_id: int) -> dict:
        """Get room weekly schedule."""
        cmd = f'rooms/{room_id}/schedule'
        data = self._hops_api_call(cmd, method="GET")
        return data

    def set_room_schedule(self, room_id: int, schedule: dict) -> dict:
        """Get room weekly schedule. Can set on day at a time. Sample payload:
        {
            "dayType": "SUNDAY",
            "daySchedule": [
                {
                    "start": "00:00",
                    "end": "07:00",
                    "dayType": "SUNDAY",
                    "setting": {
                        "power": "ON",
                        "temperature": {
                            "value": 19
                        }
                    }
                },
                {
                    "start": "07:00",
                    "end": "22:00",
                    "dayType": "SUNDAY",
                    "setting": {
                        "power": "ON",
                        "temperature": {
                            "value": 21
                        }
                    }
                },
                {
                    "start": "22:00",
                    "end": "24:00",
                    "dayType": "SUNDAY",
                    "setting": {
                        "power": "ON",
                        "temperature": {
                            "value": 19
                        }
                    }
                }
            ]
        }
        """
        cmd = f'rooms/{room_id}/schedule'
        data = self._hops_api_call(cmd, method="POST", data=schedule)
        return data


    # Ctor
    def __init__(self, username, password):
        """Performs login and save session cookie."""
        # HTTPS Interface

        cj = CookieJar()

        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cj),
            urllib.request.HTTPSHandler())
        self._login_v2(username, password)
        self.id = self.get_me()['homes'][0]['id']
