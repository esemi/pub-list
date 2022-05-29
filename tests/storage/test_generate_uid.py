from publist.storage import redis_helpers


def test_generate_uid_happy_path():
    res1 = redis_helpers.generate_uid()
    res2 = redis_helpers.generate_uid()

    assert isinstance(res1, str)
    assert isinstance(res2, str)
    assert res1 != res2
