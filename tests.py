from test_credentials import tado_instance


def test_get_me_keys(tado_instance):
    result = tado_instance.get_me()

    expected_keys = ['name', 'email', 'username', 'id', 'homes', 'locale', 'mobileDevices']

    for key in expected_keys:
        assert key in result