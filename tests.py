from test_credentials import tado_instance
import datetime


def test_get_me(tado_instance):
    result = tado_instance.get_me()
    assert isinstance(result, dict)
    expected_keys = ['name', 'email', 'username', 'id', 'homes', 'locale', 'mobileDevices']
    for key in expected_keys:
        assert key in result


def test_get_rooms_and_devices(tado_instance):
    result = tado_instance.get_rooms_and_devices()
    assert isinstance(result, dict)
    expected_keys = ['rooms', 'otherDevices']
    for key in expected_keys:
        assert key in result


def test_get_rooms(tado_instance):
    result = tado_instance.get_rooms()
    assert isinstance(result, list)
    for room in result:
        expected_keys = ['id', 'name']
        assert isinstance(room['id'], int)
        for key in expected_keys:
            assert key in room


def test_get_room(tado_instance):
    room = tado_instance.get_room(1)
    expected_keys = ['id', 'name']
    assert isinstance(room['id'], int)
    for key in expected_keys:
        assert key in room


def test_get_room_day_report(tado_instance):
    report = tado_instance.get_room_day_report(1, datetime.date.today())
    expected_keys = ['zoneType', 'interval', 'hoursInDay', 'measuredData', 'stripes', 'settings', 'callForHeat', 'weather']
    assert isinstance(report, dict)
    for key in expected_keys:
        assert key in report


# def test_get_room_day_report_w_datetime(tado_instance):
#     report = tado_instance.get_room_day_report(1, datetime.datetime.now())
#     expected_keys = ['zoneType', 'interval', 'hoursInDay', 'measuredData', 'stripes', 'settings', 'callForHeat', 'weather']
#     assert isinstance(report, dict)
#     for key in expected_keys:
#         assert key in report
#
#
# def test_get_room_day_report_w_pendulum(tado_instance):
#     report = tado_instance.get_room_day_report(1, pendulum.now())
#     expected_keys = ['zoneType', 'interval', 'hoursInDay', 'measuredData', 'stripes', 'settings', 'callForHeat', 'weather']
#     assert isinstance(report, dict)
#     for key in expected_keys:
#         assert key in report


def test_get_air_comfort(tado_instance):
    report = tado_instance.get_air_comfort()
    expected_keys = ['freshness', 'comfort']
    assert isinstance(report, dict)
    for key in expected_keys:
        assert key in report


def test_get_tado_mode(tado_instance):
    mode = tado_instance.get_tado_mode()
    assert isinstance(mode, str)


def test_set_away(tado_instance):
    response = tado_instance.set_away()
    mode = tado_instance.get_tado_mode()
    assert mode == "AWAY"
    assert response is None


def test_set_home(tado_instance):
    response = tado_instance.set_home()
    mode = tado_instance.get_tado_mode()
    assert mode == "HOME"
    assert response is None


def test_boost_heating(tado_instance):
    response = tado_instance.boost_heating()
    boost_mode = tado_instance.get_rooms()[0].get('boostMode')
    assert boost_mode is not None
    assert response is None


def test_disable_heating(tado_instance):
    response = tado_instance.disable_heating()
    power = tado_instance.get_rooms()[0]['setting'].get('power')
    assert power == 'OFF'
    assert response is None


def test_resume_schedule(tado_instance):
    response = tado_instance.resume_schedule()
    room = tado_instance.get_rooms()[0]
    power = room['setting'].get('power')
    boost_mode = room.get('boostMode')
    assert power == 'ON'
    assert boost_mode is None
    assert response is None


def test_get_room_schedule(tado_instance):
    schedule = tado_instance.get_room_schedule(1)
    expected_keys = ['room', 'otherRooms', 'schedule']
    assert isinstance(schedule, dict)
    for key in expected_keys:
        assert key in schedule


def test_set_room_schedule(tado_instance):
    data = {
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
    response = tado_instance.set_room_schedule(1, schedule=data)
    assert response is None
    schedule = tado_instance.get_room_schedule(1)['schedule']
    assert data['daySchedule'][0] in schedule


